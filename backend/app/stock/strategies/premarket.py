"""默认策略：盘前动量 + 量价齐升（数据源 AKShare 东财，新浪财经兜底）。
数据获取与筛选逻辑分离，筛选为纯函数便于单测。
"""
from ..base import ScreeningStrategy, StockPick, StrategyContext, register

# 风险等级 -> 目标价涨幅
_TARGET_PCT = {"low": 0.05, "medium": 0.08, "high": 0.12}

_REQUIRED_COLS = ("代码", "名称", "最新价", "涨跌幅", "换手率", "量比",
                  "市盈率-动态", "总市值")


def _fetch_em():
    """东方财富实时行情快照（AKShare）。"""
    import akshare as ak
    return ak.stock_zh_a_spot_em()


def _fetch_sina():
    """兜底：新浪财经 A 股列表，字段对齐筛选所需列（无逐只量比，留空）。"""
    import requests
    import pandas as pd

    rows, page = [], 1
    url = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
           "Market_Center.getHQNodeData")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "Referer": "https://finance.sina.com.cn"}
    while True:
        params = {"page": page, "num": 80, "sort": "changepercent", "asc": 0,
                  "node": "hs_a", "symbol": "", "_s_r_a": "init"}
        r = requests.get(url, params=params, headers=headers, timeout=15)
        data = r.json()
        if not data:
            break
        rows.extend(data)
        if len(data) < 80 or page >= 80:
            break
        page += 1

    df = pd.DataFrame(rows)
    df = df.rename(columns={
        "code": "代码", "name": "名称", "trade": "最新价",
        "changepercent": "涨跌幅", "turnoverratio": "换手率",
        "per": "市盈率-动态", "mktcap": "总市值"})
    df["量比"] = pd.NA
    # 新浪市值单位为万元，统一换算为元
    df["总市值"] = pd.to_numeric(df["总市值"], errors="coerce") * 1e4
    return df[list(_REQUIRED_COLS)]


def screen(df, cap_floor: float = 6_000_000_000,
           risk_level: str = "medium") -> list[StockPick]:
    """纯函数：从行情 DataFrame 筛选标的。df 需含 _REQUIRED_COLS 列。"""
    import pandas as pd

    if df is None or df.empty:
        return []
    for col in ("最新价", "涨跌幅", "换手率", "量比", "市盈率-动态", "总市值"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["最新价"] > 0].copy()

    vol_ok = df["量比"].isna() | (df["量比"] > 1.2)  # 兜底源无量比，缺失视为通过
    cond = (
        (df["涨跌幅"].between(2, 6)) &   # 温和放量上行，规避追高
        (df["换手率"] > 3) &             # 有资金参与
        vol_ok &                        # 量能放大
        (df["市盈率-动态"] > 0) &        # 排除亏损/负估值
        (df["总市值"] > cap_floor)       # 排除微盘流动性风险
    )
    short = df[cond].nsmallest(15, "市盈率-动态")  # 取估值较低的前 15 只

    pct = _TARGET_PCT.get(risk_level, 0.08)
    picks = []
    for _, r in short.iterrows():
        try:
            reasons = [f"换手{r['换手率']:.1f}%", f"市值>{(cap_floor / 1e8):.0f}亿"]
            if pd.notna(r["量比"]):
                reasons.insert(0, f"量比{r['量比']:.1f}")
            picks.append(StockPick(
                code=str(r["代码"]),
                name=str(r["名称"]),
                target_price=round(float(r["最新价"]) * (1 + pct), 2),
                watch_period="09:30-10:00 竞价与早盘确认，14:30 前观察量能",
                reasons=reasons,
            ))
        except (KeyError, ValueError, TypeError):
            continue
    return picks


@register
class PreMarketMomentumStrategy(ScreeningStrategy):
    id = "premarket_momentum"
    name = "盘前动量 + 量价齐升（默认）"

    def run(self, ctx: StrategyContext) -> list[StockPick]:
        try:
            df = _fetch_em()
        except Exception:
            df = _fetch_sina()
        return screen(
            df,
            cap_floor=ctx.extra.get("market_cap_floor", 6_000_000_000),
            risk_level=ctx.extra.get("risk_level", "medium"))
