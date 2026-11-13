"""策略筛选逻辑离线单测（不依赖网络）。"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.stock.strategies.premarket import screen  # noqa: E402


def test_screen():
    df = pd.DataFrame([
        # 符合条件：涨4% 换手5 量比1.5 市值100亿 PE15 → 应入选
        {"代码": "600001", "名称": "测试一", "最新价": 10.0, "涨跌幅": 4.0,
         "换手率": 5.0, "量比": 1.5, "市盈率-动态": 15.0, "总市值": 1e10},
        # 涨幅过高(8%) → 排除
        {"代码": "600002", "名称": "测试二", "最新价": 20.0, "涨跌幅": 8.0,
         "换手率": 6.0, "量比": 2.0, "市盈率-动态": 10.0, "总市值": 2e10},
        # 换手率过低 → 排除
        {"代码": "600003", "名称": "测试三", "最新价": 30.0, "涨跌幅": 3.0,
         "换手率": 1.0, "量比": 1.5, "市盈率-动态": 12.0, "总市值": 3e10},
        # 市值过小 → 排除
        {"代码": "600004", "名称": "测试四", "最新价": 5.0, "涨跌幅": 4.0,
         "换手率": 5.0, "量比": 1.5, "市盈率-动态": 8.0, "总市值": 1e9},
        # 跌幅 → 排除
        {"代码": "600005", "名称": "测试五", "最新价": 8.0, "涨跌幅": -1.0,
         "换手率": 5.0, "量比": 1.5, "市盈率-动态": 9.0, "总市值": 1e10},
    ])
    picks = screen(df, cap_floor=6e9, risk_level="medium")
    assert len(picks) == 1, f"应只选出 1 只，实际 {len(picks)}"
    p = picks[0]
    assert p.code == "600001", p.code
    assert p.target_price == 10.8, p.target_price  # 10 * 1.08
    assert "量比1.5" in p.reasons
    print("OK screening logic:", p.code, p.name, "target", p.target_price, p.reasons)


if __name__ == "__main__":
    test_screen()
