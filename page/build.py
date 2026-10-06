"""把 head.part + body.part 拼成 docs/index.html，并注入地图轮廓与真实数据接入层。只在改版式时运行。"""
import os
D = os.path.dirname(os.path.abspath(__file__))
head = open(os.path.join(D, "head.part")).read()
body = open(os.path.join(D, "body.part")).read()
land = open(os.path.join(D, "land.txt")).read()

LIVE = r'''
// ===== 真实数据接入层：已接入的覆盖示例值，未接入的保留示例并标注 =====
const IDMAP={"10Y 实际利率":"us_real10y","2Y−10Y 利差":"us_2s10s","高收益债利差":"us_hy","VIX 波动率":"us_vix","标普 500":"us_spx","费城半导体指数":"us_sox",
 "10Y 国债收益率":"cn_10y","Shibor 1 周":"cn_shibor1w","沪深 300":"cn_csi300","恒生科技指数":"cn_hstech",
 "美元/人民币":"x_usdcny","中美 10Y 利差":"x_cnus10y","美元指数":"x_dxy","美元/日元":"g_usdjpy","新兴市场货币指数":"g_emfx"};
let LIVE=null;
function liveTag(real,date,note){return real?`<span class="live" title="${note||""}">真实 · ${date.slice(5)}</span>`:`<span class="mock">示例</span>`;}
function applyLive(D){LIVE=D;let n=0;
 MK.forEach(m=>{const id=IDMAP[m[1]];const x=id&&D.daily[id];if(!x)return;m[3]=x.last;m.s=x.spark;m.w=x.chg1w;m.pct=x.pct10y;m.real=true;m.date=x.date;m.note=x.note+(x.pct_years<9.5?`（分位按 ${x.pct_years} 年）`:"");m.kind=x.kind;n++;});
 C.forEach(c=>{const x=D.daily[c.id];if(!x)return;c.end=x.last;c.s=x.spark;c.d1=x.chg1d;c.w1=x.chg1w;c.m1=x.chg1m;c.y1=x.chg1y??c.y1;c.u=x.unit;c.real=true;c.date=x.date;c.note=x.note;n++;});
 const CMAP={"近月升水":"升水","远月升水":"贴水","平坦":"平坦","正常":"正常"};
 C.forEach(c=>{const k=(D.curves||{})[c.id];if(!k)return;c.cv=k.points.map(p=>p[1]);c.curve=CMAP[k.label]||k.label;c.curveReal=true;c.curveInfo=`近月 ${k.points[0][0]} 比 ${k.vs} ${k.spread_pct>0?"贵":"便宜"} ${Math.abs(k.spread_pct).toFixed(1)}%${k.chg4w!=null?`，4 周${k.chg4w>0?"走阔":"收窄"} ${Math.abs(k.chg4w).toFixed(1)} 个百分点`:""}${k.note?"（"+k.note+"）":""}`;n++;});
 CK.forEach(c=>{const x=D.chokepoints[c[0]];if(x&&x.dev!=null){c[3]=x.dev;c.real=true;c.date=x.date;n++;}});
 if(D.spreads.brent_wti){SP[0][1]=D.spreads.brent_wti.value.toFixed(2)+" $/桶";SP[0][2]="";SP[0].real=true}
 if(D.spreads.ttf_hh){SP[1][1]=D.spreads.ttf_hh.value.toFixed(2)+" $/MMBtu";SP[1][2]="";SP[1].real=true}
 const Wk=D.weekly;
 if(Wk){
  if(Object.keys(Wk.cot).length){COT.length=0;Object.entries(Wk.cot).forEach(([k,v])=>COT.push([k+(k==="原油"?" WTI":""),v.pct2y,v.chg]));n+=COT.length;}
  const wr=Object.values(Wk.warrants);for(let i=wr.length-1;i>=0;i--){const w=wr[i];INV.unshift([w.label+`（近 ${w.days} 个交易日）`,w.last.toLocaleString("en-US")+" "+w.unit,(w.chg>0?"+":"−")+Math.abs(w.chg).toLocaleString("en-US"),w.pct,w.date]);n++;}
  const WMAP={"美国初请失业金":"icsa","美联储资产负债表":"walcl","芝加哥联储金融条件指数":"nfci"};
  WM.forEach(m=>{const x=Wk.misc[WMAP[m[0]]];if(!x)return;const dg=x.unit==="万人"?1:x.unit==="万亿美元"?2:2;m[1]=x.last.toFixed(dg).replace("-","−");m[3]=x.prev!=null?x.prev.toFixed(dg).replace("-","−"):"—";m[5]="截至 "+x.date.slice(5);m.spark=x.spark;m.pct=x.pct10y;m.real=true;m.date=x.date;n++;});
  C.forEach(c=>{const r=Wk.regimes[c.id];if(!r)return;c.reg=r.label;c.read=r.read;c.cot=r.cot??null;c.inv=Wk.warrants[c.id]?Wk.warrants[c.id].pct:null;c.invLabel=Wk.warrants[c.id]?"仓单近 3 月分位":null;c.regReal=true;});
  const cd=Object.values(Wk.cot)[0];const el2=document.getElementById("weeklyAsOf");if(el2&&cd)el2.textContent=cd.date;
 }
 // 规则版要点：只用真实数据生成
 const ck=Object.entries(D.chokepoints).sort((a,b)=>a[1].dev-b[1].dev)[0];
 const mov=C.filter(c=>c.real).sort((a,b)=>Math.abs(b.w1)-Math.abs(a.w1))[0];
 const ry=D.daily.us_real10y,vx=D.daily.us_vix,sp=D.daily.x_cnus10y;
 V.length=0;
 if(ck)V.push([ck[1].dev<=-15?"crit":"ok","d",`${ck[0]}通行量 ${ck[1].dev>0?"+":""}${ck[1].dev}%`,`最近 7 天日均 ${ck[1].last7} 艘，之前 30 天日均 ${ck[1].base30} 艘。`,`PortWatch 截至 ${ck[1].date.slice(5)}`]);
 const rg=D.weekly&&Object.entries(D.weekly.regimes).find(([k,v])=>v.label!=="平稳");
 if(rg){const cc=C.find(c=>c.id===rg[0]);V.push([{"真实紧缺":"crit","资金推动":"warn","物流冲击":"crit","需求走弱":"ok"}[rg[1].label]||"ok","w",`${cc?cc.name:rg[0]}：${rg[1].label}`,rg[1].read.split("。")[0]+"。",`CFTC 截至 ${Object.values(D.weekly.cot)[0].date.slice(5)}`]);}
 else if(mov)V.push([mov.w1>0?"warn":"ok","d",`${mov.name} 1 周 ${pct(mov.w1)}`,`本周波动最大的品种，最新 ${fmt(mov.end)} ${mov.u}。`,`截至 ${mov.date.slice(5)}`]);
 if(ry)V.push([ry.pct10y>=80?"crit":"ok","d",`美国 10Y 实际利率 ${ry.last.toFixed(2)}%`,`处在过去十年 ${ry.pct10y}% 分位（${bandOf(ry.pct10y)}），全球融资成本偏${ry.pct10y>=60?"紧":"松"}。`,`FRED 截至 ${ry.date.slice(5)}`]);
 if(sp)V.push([sp.pct10y<=20?"warn":"ok","d",`中美 10Y 利差 ${Math.round(sp.last)} bp`,`处在过去十年 ${sp.pct10y}% 分位，人民币资产相对收益${sp.pct10y<=20?"处于低位":"一般"}。`,`截至 ${sp.date.slice(5)}`]);
 document.getElementById("verdict").innerHTML=V.map(v=>`<div class="sig"><div class="bar" style="background:var(${VC[v[0]]})"></div><div><h3><span class="cad ${CADN[v[1]][1]}">${CADN[v[1]][0]}</span>${v[2]}</h3><p>${v[3]}</p><p class="num" style="font-size:11px;color:var(--faint);margin-top:2px">${v[4]} · 规则自动生成</p></div></div>`).join("");
 const lastD=Object.values(D.daily).map(x=>x.date).sort().at(-1);const el=document.getElementById("dailyAsOf");if(el)el.textContent=lastD;const nx=document.getElementById("dailyNext");if(nx)nx.textContent="每天 07:00 SGT";
 document.getElementById("livebadge").textContent=`真实数据 ${n} 项 · 其余为示例`;
 document.getElementById("stamp").textContent="数据生成 "+D.generated.replace("T"," ").slice(0,16)+" UTC";
}
'''

css_add = """
.live{font-size:10.5px;font-family:var(--f-num);color:var(--ok);border:1px solid currentColor;border-radius:4px;padding:0 5px;margin-left:6px;white-space:nowrap}
.mock{font-size:10.5px;color:var(--faint);border:1px dashed var(--line);border-radius:4px;padding:0 5px;margin-left:6px;white-space:nowrap}
.banner{font-size:12.5px;color:var(--warn);background:var(--warn-soft);border-radius:8px;padding:8px 12px}
</style>"""

s = head + body
_lines = []
for ln in s.split("\n"):
    for pre, fn in [('document.getElementById("cot").innerHTML=', "renderCot"), ('document.getElementById("inv").innerHTML=', "renderInv"), ('document.getElementById("weeklyMisc").innerHTML=', "renderWM")]:
        if ln.startswith(pre):
            ln = f"function {fn}(){{" + ln + ("bindInfo(document.getElementById(\"weeklyMisc\"));" if fn == "renderWM" else "") + "}"
    if ln.startswith('bindInfo(document.getElementById("weeklyMisc"));'):
        ln = ""
    _lines.append(ln)
s = "\n".join(_lines)
s = s.replace("function renderAll(){renderQuad();", "function renderAll(){renderCot();renderInv();renderWM();renderQuad();")
# 周频小卡片支持真实数据
s = s.replace('const s=mseries(v,pv,26,m[6]);', 'const s=m.spark||mseries(v,pv,26,m[6]);')
s = s.replace('${prow((INFO["周·"+m[0]]||[])[0])}', '${prow(m.pct??(m.real?null:(INFO["周·"+m[0]]||[])[0]))}')
s = s.replace('data-cad="周"><span class="hint">?</span><div class="k">${m[0]}</div>', 'data-cad="周" data-pct="${m.pct??""}"><span class="hint">?</span><div class="k">${m[0]}${liveTag(m.real,m.date||"","")}</div>')
s = s.replace('<tr><td style="text-align:left">${r[0]}</td><td class="num">${r[1]}</td>', '<tr><td style="text-align:left">${r[0]}${r[4]?liveTag(true,r[4],""):\'<span class="mock">示例</span>\'}</td><td class="num">${r[1]}</td>')
s = s.replace("</style>", css_add, 1)
s = s.replace("__LAND__", land)
# 标签与徽章
s = s.replace('<span class="badge">示例数据 · 仅示意版式</span>', '<span class="badge" id="livebadge">示例数据 · 正在加载真实数据</span>')
s = s.replace('<span class="stamp num">页面生成 2026-10-06 07:00 SGT</span>', '<span class="stamp num" id="stamp"></span>')
s = s.replace('["中国","DR007 资金利率","%",1.52,.01,"down"]', '["中国","Shibor 1 周","%",1.52,.01,"down"]')
s = s.replace('"中国·DR007 资金利率":[15,"银行间市场 7 天回购利率，是中国短期资金的价格。","央行通过它引导资金松紧；明显高于政策利率，说明市场资金偏紧。","货币创造与加息传导"]',
              '"中国·Shibor 1 周":[15,"上海银行间同业拆借利率（1 周），反映中国银行之间的短期资金价格，这里代替 DR007。","央行通过公开市场操作引导它；明显走高说明市场资金偏紧。","货币创造与加息传导"]')
# 金融市场卡片：真实分位与标签
s = s.replace('<div class="k">${m[1]}</div><div class="v num">${fmt(m[3])}', '<div class="k">${m[1]}${liveTag(m.real,m.date||"",m.note)}</div><div class="v num">${fmt(m[3])}')
s = s.replace('${prow((INFO[m[0]+"·"+m[1]]||[])[0])}</button>', '${prow(m.pct??(m.real?null:(INFO[m[0]+"·"+m[1]]||[])[0]))}</button>')
s = s.replace('data-info="${m[0]}·${m[1]}" data-val="${fmt(m[3])}"', 'data-info="${m[0]}·${m[1]}" data-pct="${m.pct??""}" data-val="${fmt(m[3])}"')
# 说明抽屉使用真实分位
s = s.replace('function bindInfo(root){root.querySelectorAll("[data-info]").forEach(b=>b.onclick=()=>openInfo(b.dataset.info,b.dataset.val,b.dataset.unit,b.dataset.cad));}',
              'function bindInfo(root){root.querySelectorAll("[data-info]").forEach(b=>b.onclick=()=>{const I=INFO[b.dataset.info];if(I&&b.dataset.pct!=="")I[0]=+b.dataset.pct;openInfo(b.dataset.info,b.dataset.val,b.dataset.unit,b.dataset.cad)});}')
s = s.replace('分位为示例数据。真实版按过去十年的日度或月度数据计算。', '标「真实」的指标按过去十年数据计算分位；标「示例」的仍是模拟值。')
# 热力表与卡片：真实标签
s = s.replace('<td class="name">${c.name}<small>${c.u} · ${c.g}</small></td>', '<td class="name">${c.name}${liveTag(c.real,c.date||"",c.note)}<small>${c.u} · ${c.g}</small></td>')
s = s.replace('点击表头排序，点击任一行打开详情。红涨绿跌。持仓和库存是周度数据，在「周频」面板。', '点击表头排序，点击任一行打开详情。红涨绿跌。期限结构一列仍是示例，第 2 阶段接入；持仓和库存是周度数据，在「周频」面板。')
s = s.replace('数据截至 <b class="num">2026-10-05 收盘</b></span><span>下次更新 <b class="num">10-07 07:00</b>', '数据截至 <b class="num" id="dailyAsOf">—</b></span><span>更新时间 <b class="num" id="dailyNext">—</b>')
s = s.replace('<td>${curvePill(c.curve)}</td>', '<td title="${c.curveInfo||""}">${curvePill(c.curve)}${c.curveReal?"":"<span class=\\"mock\\">示例</span>"}</td>')
s = s.replace('期限结构一列仍是示例，第 2 阶段接入；', '期限结构：近月合约对第 6 个月合约（天然气对 12 个月后），差价超过 1.5% 判为升水；鼠标悬停看具体价差。')
s = s.replace('<div class="fact"><span class="k">期限结构 M1→M12</span>${curveSvg(c.cv)}</div>', '<div class="fact"><span class="k">期限结构 M1→M12${c.curveReal?"":" · 示例"}</span>${curveSvg(c.cv)}</div>')
s = s.replace('c.curve==="升水"?"近月升水：现货偏紧":c.curve==="贴水"?"远月升水：供应宽松":c.curve}</div>', 'c.curve==="升水"?"近月升水：现货偏紧":c.curve==="贴水"?"远月升水：供应宽松":c.curve}</div>${c.curveInfo?`<div style="font-size:12px;color:var(--muted);margin-top:4px">${c.curveInfo}</div>`:""}')
s = s.replace('<div class="fact"><span class="k">库存 vs 5 年同期</span>', '<div class="fact"><span class="k">${c.invLabel||"库存 vs 5 年同期"}</span>')
# 咽喉
s = s.replace('<div class="note">每日通行船数 vs 30 日均值</div>', '<div class="note" id="cknote">最近 7 天日均通行船数 vs 之前 30 天日均（IMF PortWatch，约滞后一周）</div>')
# 非日频面板横幅
s = s.replace('<div class="pane" id="p-weekly" role="tabpanel" aria-labelledby="t-weekly" hidden>', '<div class="pane" id="p-weekly" role="tabpanel" aria-labelledby="t-weekly" hidden>\n    <div class="banner">CFTC 持仓、交易所仓单、美联储周度数据和品种判断已接入真实数据；EIA 原油库存、欧洲天然气库存、SCFI 运价、中国港口铁矿库存仍为示例（前两项需要注册免费 key，后两项为付费数据）。</div>')
s = s.replace('本周判断基于 <b class="num">2026-10-03</b> 前数据', '持仓数据截至 <b class="num" id="weeklyAsOf">—</b>')
s = s.replace('<div class="pane" id="p-monthly" role="tabpanel" aria-labelledby="t-monthly" hidden>', '<div class="pane" id="p-monthly" role="tabpanel" aria-labelledby="t-monthly" hidden>\n    <div class="banner">本面板仍为示例数据，第 4 阶段接入。</div>')
s = s.replace('<div class="pane" id="p-news" role="tabpanel" aria-labelledby="t-news" hidden>', '<div class="pane" id="p-news" role="tabpanel" aria-labelledby="t-news" hidden>\n    <div class="banner">本面板仍为示例新闻，第 6 阶段接入。</div>')
s = s.replace('<h2>经济周期：中美两国在哪一格</h2>', '<h2>经济周期：中美两国在哪一格 <span class="mock">示例 · 第 4 阶段接入</span></h2>')
s = s.replace('本页所有数字和新闻条目均为模拟生成，用于展示看板的理想形态，不代表真实市场或真实事件。', '标「真实」的数字来自 FRED、Yahoo Finance、AKShare、IMF PortWatch，每天自动更新；标「示例」的数字和全部新闻条目仍为模拟，会分阶段替换。代码：github.com/liquan-zhang/world-monitor')
# 启动：先取数据再渲染
s = s.replace("renderAll();show(start);", "show(start);fetch(\"data/latest.json\",{cache:\"no-store\"}).then(r=>r.ok?r.json():Promise.reject(r.status)).then(D=>{applyLive(D);renderAll();}).catch(e=>{document.getElementById(\"livebadge\").textContent=\"真实数据加载失败 · 显示示例\";renderAll();});")
s = s.replace("// 标签页", LIVE + "\n// 标签页", 1)
# 真实数据的变化量：利率类用绝对值
s = s.replace('<div class="d num ${cls(m.w)}">1 周 ${pct(m.w)}</div>', '<div class="d num ${cls(m.w)}">1 周 ${m.kind==="abs"?(m.w>0?"+":"")+(m[2]==="bp"?m.w.toFixed(0)+" bp":m.w.toFixed(2)+" pct"):pct(m.w)}</div>')
SKEL_HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>
"""
s = SKEL_HEAD + s.replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1) + "\n</body>\n</html>\n"
open(os.path.join(os.path.dirname(D), "docs", "index.html"), "w").write(s)
print("built docs/index.html", len(s))
