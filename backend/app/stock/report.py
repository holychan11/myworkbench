"""盘前报告渲染（微信推送格式）。"""


def build_report(strategy_name: str, trade_date: str, picks) -> str:
    header = f"📈 MyWorkbench 盘前报告（{trade_date}）"
    if not picks:
        return (f"{header}\n{'-' * 24}\n"
                "今日策略未选出符合条件的标的，可稍后手动重试。\n"
                "⚠️ 本报告由策略模型生成，不构成投资建议")
    lines = [header, "-" * 24, f"策略：{strategy_name}", ""]
    for i, p in enumerate(picks, 1):
        lines.append(f"{i}. {p.code} {p.name}")
        lines.append(f"   参考目标价：{p.target_price:.2f}")
        lines.append(f"   建议关注时段：{p.watch_period}")
        lines.append(f"   入选理由：{' / '.join(p.reasons)}")
    lines.append("")
    lines.append("⚠️ 本报告由策略模型生成，不构成投资建议")
    return "\n".join(lines)
