"""数据源。每个函数返回 [[YYYY-MM-DD, float], ...]，按日期升序。单个源失败由调用方处理。"""
import csv, io, json, subprocess, datetime as dt, warnings
warnings.filterwarnings("ignore")

H_CURL = {"User-Agent": "curl/8.7.1", "Accept": "*/*"}
H_BROWSER = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
TIMEOUT = 40


def _get(url, headers=None, params=None):
    import requests
    headers = headers or H_CURL
    try:
        r = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        if params:
            raise
        # 本机企业网络下 requests 偶尔失败，系统 curl 兜底
        out = subprocess.run(["curl", "-sSL", "--max-time", str(TIMEOUT), "-H", f"User-Agent: {headers['User-Agent']}", url],
                             capture_output=True, text=True, timeout=TIMEOUT + 10)
        if out.returncode != 0 or not out.stdout:
            raise RuntimeError(f"curl failed rc={out.returncode}")
        return out.stdout


def fred(series_id):
    txt = _get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}")
    out = []
    for r in list(csv.reader(io.StringIO(txt)))[1:]:
        if len(r) >= 2 and r[1] not in (".", ""):
            try:
                out.append([r[0], float(r[1])])
            except ValueError:
                pass
    return out


def yahoo(symbol, rng="10y"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={rng}&interval=1d"
    d = json.loads(_get(url, H_BROWSER))["chart"]["result"][0]
    out = {}
    for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]):
        if c is not None:
            out[dt.datetime.utcfromtimestamp(t).date().isoformat()] = float(c)
    return sorted(out.items())


def _df_series(df, dcol, vcol):
    out = []
    for _, r in df.iterrows():
        v = r[vcol]
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if v != v:  # NaN（节假日空行）
            continue
        out.append([str(r[dcol])[:10], v])
    out.sort()
    return out


_bond_cache = {}
def bond_zh_us(col):
    import akshare as ak
    if "df" not in _bond_cache:
        _bond_cache["df"] = ak.bond_zh_us_rate(start_date="20150101")
    return _df_series(_bond_cache["df"], "日期", col)


def cn_index(symbol):
    import akshare as ak
    return _df_series(ak.stock_zh_index_daily(symbol=symbol), "date", "close")


def hk_index(symbol):
    import akshare as ak
    return _df_series(ak.stock_hk_index_daily_sina(symbol=symbol), "date", "close")


def cn_future(symbol):
    import akshare as ak
    return _df_series(ak.futures_main_sina(symbol=symbol), "日期", "收盘价")


def shibor_1w():
    import akshare as ak
    return _df_series(ak.rate_interbank(market="上海银行同业拆借市场", symbol="Shibor人民币", indicator="1周"), "报告日", "利率")


PORTWATCH = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query"
def portwatch(portnames, days=75):
    """IMF PortWatch 每日咽喉通行船数。返回 {portname: [[date, n_total], ...]}"""
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    names = ",".join(f"'{p}'" for p in portnames)
    out = {p: [] for p in portnames}
    offset = 0
    while True:
        txt = _get(PORTWATCH, params={"where": f"portname IN ({names}) AND date >= '{since}'", "outFields": "date,portname,n_total",
                                      "orderByFields": "date ASC", "resultOffset": offset, "resultRecordCount": 2000, "f": "json"})
        feats = json.loads(txt).get("features", [])
        for f in feats:
            a = f["attributes"]
            out[a["portname"]].append([str(a["date"])[:10], float(a["n_total"])])
        if len(feats) < 2000:
            break
        offset += 2000
    return out


MONTHS = "FGHJKMNQUVXZ"
def yahoo_curve(root, exch, n=13, scale=1.0, start=None):
    """Yahoo 单月合约曲线，返回 [[YYMM, price], ...]，按到期先后。"""
    start = start or dt.date.today()
    out = []
    for k in range(0, n + 3):
        mi = (start.month - 1 + k) % 12
        yy = (start.year + (start.month - 1 + k) // 12) % 100
        sym = f"{root}{MONTHS[mi]}{yy:02d}.{exch}"
        try:
            d = json.loads(_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d", H_BROWSER))["chart"]["result"][0]
            c = [x for x in d["indicators"]["quote"][0]["close"] if x is not None]
            if c:
                out.append([f"{yy:02d}{mi + 1:02d}", round(c[-1] * scale, 4)])
        except Exception:
            continue
        if len(out) >= n:
            break
    return out


def cn_curve(root, n=12, start=None):
    """国内期货分月合约曲线（AKShare 新浪源），剔除停止交易的合约。"""
    import akshare as ak
    start = start or dt.date.today()
    rows = []
    for k in range(0, n + 2):
        y = start.year + (start.month - 1 + k) // 12
        m = (start.month - 1 + k) % 12 + 1
        sym = f"{root}{y % 100:02d}{m:02d}"
        try:
            df = ak.futures_zh_daily_sina(symbol=sym)
            if len(df):
                rows.append([f"{y % 100:02d}{m:02d}", float(df["close"].iloc[-1]), str(df["date"].iloc[-1])[:10]])
        except Exception:
            continue
    if not rows:
        return []
    latest = max(r[2] for r in rows)
    cutoff = (dt.date.fromisoformat(latest) - dt.timedelta(days=10)).isoformat()
    return [[a, b] for a, b, d in rows if d >= cutoff][:n]
