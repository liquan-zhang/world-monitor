# 世界经济监控台

以中美两极为主轴、按更新频率分面板的世界经济看板。网页：https://liquan-zhang.github.io/world-monitor/

- `pipeline/`：每天抓数（FRED、Yahoo Finance、AKShare、IMF PortWatch），计算涨跌与十年分位，写 `docs/data/latest.json`
- `page/`：网页源码，改版式后运行 `python page/build.py` 生成 `docs/index.html`
- `.github/workflows/update.yml`：每天 07:00（新加坡时间）自动运行

接入进度：第 1 阶段（架构）与第 2 阶段（日频价格）已完成；期限结构、周频、月频、判断层、新闻依次接入。标「示例」的数字仍为模拟。
