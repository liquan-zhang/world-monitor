"""指标目录。加指标只改这里。
kind: pct = 变化用百分比（价格、指数）；abs = 变化用绝对值（利率、利差）
"""
from sources import fred, yahoo, bond_zh_us, cn_index, hk_index, cn_future, shibor_1w

LB_PER_T = 2204.62

DAILY = {
    # 金融市场
    "us_real10y": dict(fn=lambda: fred("DFII10"), unit="%", kind="abs"),
    "us_2s10s":   dict(fn=lambda: fred("T10Y2Y"), unit="bp", kind="abs", scale=100),
    "us_hy":      dict(fn=lambda: fred("BAMLH0A0HYM2"), unit="bp", kind="abs", scale=100, note="FRED 自 2023 年起只提供近 3 年数据，分位按 3 年计算"),
    "us_vix":     dict(fn=lambda: fred("VIXCLS"), unit="", kind="pct"),
    "us_spx":     dict(fn=lambda: fred("SP500"), unit="", kind="pct"),
    "us_sox":     dict(fn=lambda: yahoo("^SOX"), unit="", kind="pct"),
    "cn_10y":     dict(fn=lambda: bond_zh_us("中国国债收益率10年"), unit="%", kind="abs"),
    "cn_shibor1w":dict(fn=shibor_1w, unit="%", kind="abs", note="以 Shibor 1 周代替 DR007"),
    "cn_csi300":  dict(fn=lambda: cn_index("sh000300"), unit="", kind="pct"),
    "cn_hstech":  dict(fn=lambda: hk_index("HSTECH"), unit="", kind="pct"),
    "x_usdcny":   dict(fn=lambda: yahoo("CNY=X"), unit="", kind="pct"),
    "x_dxy":      dict(fn=lambda: yahoo("DX-Y.NYB"), unit="", kind="pct"),
    "g_usdjpy":   dict(fn=lambda: yahoo("JPY=X"), unit="", kind="pct"),
    "g_emfx":     dict(fn=lambda: yahoo("CEW"), unit="", kind="pct", note="以 WisdomTree 新兴市场货币基金 CEW 代替指数"),
    # 商品（连续主力合约）
    "brent": dict(fn=lambda: yahoo("BZ=F"), unit="$/桶", kind="pct"),
    "wti":   dict(fn=lambda: yahoo("CL=F"), unit="$/桶", kind="pct"),
    "hh":    dict(fn=lambda: yahoo("NG=F"), unit="$/MMBtu", kind="pct"),
    "ttf":   dict(fn=lambda: yahoo("TTF=F"), unit="€/MWh", kind="pct"),
    "cu":    dict(fn=lambda: [[d, v * LB_PER_T] for d, v in yahoo("HG=F")], unit="$/吨", kind="pct", note="COMEX 铜换算为美元/吨"),
    "al":    dict(fn=lambda: yahoo("ALI=F"), unit="$/吨", kind="pct", note="COMEX 铝"),
    "fe":    dict(fn=lambda: cn_future("I0"), unit="元/吨", kind="pct", note="大商所铁矿石主力合约"),
    "li":    dict(fn=lambda: cn_future("LC0"), unit="元/吨", kind="pct"),
    "au":    dict(fn=lambda: yahoo("GC=F"), unit="$/盎司", kind="pct"),
    "ag":    dict(fn=lambda: yahoo("SI=F"), unit="$/盎司", kind="pct"),
    "soy":   dict(fn=lambda: yahoo("ZS=F"), unit="美分/蒲式耳", kind="pct"),
    "wheat": dict(fn=lambda: yahoo("ZW=F"), unit="美分/蒲式耳", kind="pct"),
    # 只用于计算
    "_us10y":  dict(fn=lambda: bond_zh_us("美国国债收益率10年"), unit="%", kind="abs", hidden=True),
    "_eurusd": dict(fn=lambda: yahoo("EURUSD=X"), unit="", kind="pct", hidden=True),
}

CHOKEPOINTS = {"Strait of Hormuz": "霍尔木兹", "Bab el-Mandeb Strait": "曼德", "Suez Canal": "苏伊士", "Malacca Strait": "马六甲",
               "Panama Canal": "巴拿马", "Cape of Good Hope": "好望角", "Bosporus Strait": "土耳其海峡", "Taiwan Strait": "台湾海峡"}

from sources import yahoo_curve, cn_curve
# 期限结构。cmp：用第几个合约和近月比较（季节性品种比 12 个月后）；carry：远月贵属正常（黄金）
CURVES = {
    "brent": dict(fn=lambda: yahoo_curve("BZ", "NYM"), cmp=5),
    "wti":   dict(fn=lambda: yahoo_curve("CL", "NYM"), cmp=5),
    "hh":    dict(fn=lambda: yahoo_curve("NG", "NYM"), cmp=12, note="天然气有季节性，比较近月与 12 个月后的同月合约"),
    "cu":    dict(fn=lambda: yahoo_curve("HG", "CMX", scale=LB_PER_T), cmp=5),
    "au":    dict(fn=lambda: yahoo_curve("GC", "CMX"), cmp=5, carry=True, note="远月贵是持有成本，属正常"),
    "fe":    dict(fn=lambda: cn_curve("I"), cmp=5),
    "li":    dict(fn=lambda: cn_curve("LC"), cmp=5),
}
