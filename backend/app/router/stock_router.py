"""A股：策略列表 / 手动触发 / 历史报告 / 订阅偏好。"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..stock.base import all_strategies

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("/strategies")
def strategies():
    return [{"id": s.id, "name": s.name} for s in all_strategies().values()]


@router.post("/run", response_model=schemas.StockRunOut)
def run_now(request: Request, user: models.User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    d = request.app.state.dispatcher
    report = d._report(db, user)
    return schemas.StockRunOut(
        strategy_id="premarket_momentum",
        trade_date=datetime.now().strftime("%Y-%m-%d"), report=report)


@router.get("/reports")
def reports(user: models.User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    rows = (db.query(models.StockReport)
            .filter_by(user_id=user.id)
            .order_by(models.StockReport.id.desc()).limit(50).all())
    return [{
        "id": r.id, "strategy_id": r.strategy_id, "trade_date": r.trade_date,
        "picks": json.loads(r.picks or "[]"),
        "created_at": str(r.created_at),
    } for r in rows]


@router.get("/prefs")
def get_prefs(user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    p = db.get(models.UserPref, user.id)
    if not p:
        return {"premarket_enabled": False, "premarket_strategy": "premarket_momentum",
                "risk_level": "medium"}
    return {"premarket_enabled": p.premarket_enabled,
            "premarket_strategy": p.premarket_strategy, "risk_level": p.risk_level}


@router.put("/prefs")
def set_prefs(data: schemas.PrefsIn, user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    p = db.get(models.UserPref, user.id)
    if not p:
        p = models.UserPref(user_id=user.id)
        db.add(p)
    p.premarket_enabled = data.premarket_enabled
    p.premarket_strategy = data.premarket_strategy
    p.risk_level = data.risk_level
    db.commit()
    return {"ok": True}
