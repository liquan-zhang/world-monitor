"""每日任务：抓取 → 计算 → 写 docs/data/latest.json。单个指标失败只记录，不中断。"""
import json, sys, os, datetime as dt, traceback
sys.path.insert(0, os.path.dirname(__file__))
from catalog import DAILY, CHOKEPOINTS, CURVES
from sources import portwatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "data", "latest.json")
CURVE_HIST = os.path.join(ROOT, "docs", "data", "curve_history.json")
SPARK_N = 260


def stats(series, kind, scale=1.0):
    s = [[d, v * scale] for d, v in series]
    last_d, last = s[-1]
    def back(n):
        return s[-1 - n][1] if len(s) > n else None
    def chg(n):
        p = back(n)
        if p is None:
            return None
        return (last / p - 1) * 100 if kind == "pct" and p else last - p
    cutoff = (dt.date.fromisoformat(last_d) - dt.timedelta(days=3652)).isoformat()
    win = [v for d, v in s if d >= cutoff]
    pct = round(100 * sum(1 for v in win if v < last) / max(len(win) - 1, 1)) if len(win) > 20 else None
    first_in = [d for d, _ in s if d >= cutoff][0]
    years = round((dt.date.fromisoformat(last_d) - dt.date.fromisoformat(first_in)).days / 365.25, 1)
    tail = s[-SPARK_N:]
    return dict(last=round(last, 4), date=last_d, prev=round(back(1), 4) if back(1) is not None else None,
                chg1d=_r(chg(1)), chg1w=_r(chg(5)), chg1m=_r(chg(21)), chg1y=_r(chg(252)),
                pct10y=pct, pct_years=years, spark=[round(v, 4) for _, v in tail], spark_from=tail[0][0])


def _r(x):
    return None if x is None else round(x, 3)


def main():
    out = dict(generated=dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), daily={}, chokepoints={}, spreads={}, errors=[])
    raw = {}
    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT)).get("daily", {})
        except Exception:
            prev = {}
    for k, spec in DAILY.items():
        try:
            ser = spec["fn"]()
            if len(ser) < 30:
                raise ValueError(f"only {len(ser)} points")
            raw[k] = ser
            if spec.get("hidden"):
                continue
            st = stats(ser, spec["kind"], spec.get("scale", 1.0))
            st.update(unit=spec["unit"], kind=spec["kind"], note=spec.get("note", ""))
            out["daily"][k] = st
            print(f"ok   {k:12s} {st['date']} {st['last']}")
        except Exception as e:
            out["errors"].append(f"{k}: {str(e)[:120]}")
            print(f"FAIL {k:12s} {e}")
            if k in prev:  # 沿用上次成功的数据，并标注
                old = dict(prev[k]); old["stale"] = True
                old["note"] = (old.get("note", "") + " 本次抓取失败，沿用上次数据").strip()
                out["daily"][k] = old

    # 派生：中美 10Y 利差（bp）
    try:
        cn, us = dict(raw["cn_10y"]), dict(raw["_us10y"])
        ser = [[d, cn[d] - us[d]] for d in sorted(cn) if d in us]
        st = stats(ser, "abs", 100); st.update(unit="bp", kind="abs", note="中国 10 年期减美国 10 年期")
        out["daily"]["x_cnus10y"] = st
    except Exception as e:
        out["errors"].append(f"x_cnus10y: {e}")

    # 价差
    def last_of(k):
        return raw[k][-1][1] if k in raw else None
    try:
        out["spreads"]["brent_wti"] = dict(label="布伦特 − WTI", value=round(last_of("brent") - last_of("wti"), 2), unit="$/桶")
    except Exception as e:
        out["errors"].append(f"spread brent_wti: {e}")
    try:
        ttf_usd = last_of("ttf") * last_of("_eurusd") / 3.412  # 1 MWh = 3.412 MMBtu
        out["spreads"]["ttf_hh"] = dict(label="欧洲 TTF − 美国 HH", value=round(ttf_usd - last_of("hh"), 2), unit="$/MMBtu")
    except Exception as e:
        out["errors"].append(f"spread ttf_hh: {e}")

    # 咽喉：最近 7 天均值 vs 之前 30 天均值
    try:
        pw = portwatch(list(CHOKEPOINTS))
        for en, zh in CHOKEPOINTS.items():
            s = pw.get(en, [])
            if len(s) < 37:
                out["errors"].append(f"portwatch {en}: only {len(s)} days"); continue
            last7 = sum(v for _, v in s[-7:]) / 7
            base = sum(v for _, v in s[-37:-7]) / 30
            out["chokepoints"][zh] = dict(en=en, last7=round(last7, 1), base30=round(base, 1),
                                          dev=round((last7 / base - 1) * 100) if base else None, date=s[-1][0])
        print("ok   chokepoints", {k: v["dev"] for k, v in out["chokepoints"].items()})
    except Exception as e:
        out["errors"].append(f"portwatch: {e}")

    # 期限结构：近月 vs 第 cmp 个合约，价差占近月的百分比；每日存档以判断走阔或收窄
    out["curves"] = {}
    hist = json.load(open(CURVE_HIST)) if os.path.exists(CURVE_HIST) else {}
    today = dt.date.today().isoformat()
    for k, spec in CURVES.items():
        try:
            pts = spec["fn"]()
            if len(pts) < 6:
                raise ValueError(f"only {len(pts)} contracts")
            i = min(spec["cmp"], len(pts) - 1)
            m1, mx = pts[0][1], pts[i][1]
            spread = round((m1 - mx) / m1 * 100, 2)
            if spec.get("carry"):
                label = "近月升水" if spread > 0.3 else "正常"
            else:
                label = "近月升水" if spread > 1.5 else "远月升水" if spread < -1.5 else "平坦"
            h = [r for r in hist.get(k, []) if r[0] != today] + [[today, spread]]
            hist[k] = h[-400:]
            old = [v for d, v in h if d <= (dt.date.today() - dt.timedelta(days=28)).isoformat()]
            chg4w = round(spread - old[-1], 2) if old else None
            out["curves"][k] = dict(points=pts, label=label, spread_pct=spread, vs=pts[i][0], chg4w=chg4w, note=spec.get("note", ""))
            print(f"ok   curve {k:6s} {label} {spread:+.2f}% ({pts[0][0]} vs {pts[i][0]})")
        except Exception as e:
            out["errors"].append(f"curve {k}: {str(e)[:100]}")
            print(f"FAIL curve {k}: {e}")
    with open(CURVE_HIST, "w") as f:
        json.dump(hist, f, separators=(",", ":"))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}  indicators={len(out['daily'])}  errors={len(out['errors'])}")


if __name__ == "__main__":
    main()
