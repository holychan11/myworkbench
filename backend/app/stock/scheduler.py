"""盘前报告定时调度：每交易日 08:30（交易日历用 AKShare，异常时兜底为周一~周五）。"""
import json
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config import settings
from .base import StrategyContext, get_strategy
from .report import build_report

_scheduler: BackgroundScheduler | None = None


def is_trade_day(d: datetime) -> bool:
    try:
        import akshare as ak
        cal = ak.tool_trade_date_hist_sina()
        return d.strftime("%Y-%m-%d") in set(cal["trade_date"].astype(str))
    except Exception:  # noqa: BLE001
        return d.weekday() < 5  # 兜底：周一至周五


def run_premarket_report(gateway) -> None:
    from .. import models
    from ..core.audit import log
    from ..database import SessionLocal

    now = datetime.now()
    if not is_trade_day(now):
        return
    trade_date = now.strftime("%Y-%m-%d")
    db = SessionLocal()
    try:
        subs = db.query(models.UserPref).filter_by(premarket_enabled=True).all()
        for p in subs:
            user = db.get(models.User, p.user_id)
            if not user or not user.is_active:
                continue
            binding = db.get(models.WechatBinding, p.user_id)
            if not binding:
                continue
            strat = get_strategy(p.premarket_strategy) or get_strategy("premarket_momentum")
            ctx = StrategyContext(trade_date=trade_date,
                                  extra={"risk_level": p.risk_level, "user_id": p.user_id})
            try:
                picks = strat.run(ctx)
            except Exception as e:  # noqa: BLE001
                log(db, p.user_id, "report", status="failed", result=str(e)[:500])
                continue
            report = build_report(strat.name, trade_date, picks)
            db.add(models.StockReport(
                user_id=p.user_id, strategy_id=strat.id, trade_date=trade_date,
                picks=json.dumps([vars(x) for x in picks], ensure_ascii=False)))
            db.commit()
            gateway.send_card(binding.wx_id, "📈 MyWorkbench 盘前报告", report)
            log(db, p.user_id, "report", status="ok", result=f"推送 {len(picks)} 只标的")
    finally:
        db.close()


def start_scheduler(gateway) -> None:
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler(timezone=settings.TZ)
    _scheduler.add_job(
        run_premarket_report,
        CronTrigger(hour=settings.SCHEDULE_HOUR, minute=settings.SCHEDULE_MINUTE),
        args=[gateway], id="premarket", coalesce=True,
        misfire_grace_time=3600, replace_existing=True)
    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
