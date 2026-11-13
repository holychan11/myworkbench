"""网关交互：模拟收发（本地测试通道）、二次确认。"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db
from ..executor import confirmation, sandbox
from ..core.audit import log

router = APIRouter(prefix="/api/gateway", tags=["gateway"])


@router.post("/simulate")
def simulate(data: schemas.SimulateIn, request: Request, db: Session = Depends(get_db)):
    """模拟微信发消息（本地测试通道）。返回机器人回复。"""
    d = request.app.state.dispatcher
    reply = d.dispatch(db, data.wx_id, data.nick, data.text)
    return {"reply": reply}


@router.get("/outbox")
def outbox(request: Request, wx_id: str | None = None):
    """读取机器人待投递消息（本地测试通道，模拟手机端）。"""
    g = request.app.state.gateway
    drain = getattr(g, "drain", None)
    if drain is None:
        return []
    return drain(wx_id)


@router.post("/confirm")
def confirm(data: schemas.ConfirmIn, request: Request, db: Session = Depends(get_db)):
    """Web 端直接确认危险操作（wx_id + confirm_id）。"""
    b = db.query(models.WechatBinding).filter_by(wx_id=data.wx_id).first()
    if not b:
        return {"reply": "该微信尚未绑定。"}
    c, err = confirmation.resolve(db, b.user_id, data.confirm_id, approve=True)
    if err:
        return {"reply": err}
    r = sandbox.execute(c.cmd)
    log(db, b.user_id, "exec", cmd=c.cmd, risk=c.risk,
        status="ok" if r.ok else "failed", result=r.stdout or r.stderr)
    return {"reply": f"✅ 已执行\n{r.stdout.strip()}" if r.ok
            else f"❌ 执行失败\n{r.stderr.strip()}"}


@router.post("/cancel")
def cancel(data: schemas.ConfirmIn, request: Request, db: Session = Depends(get_db)):
    b = db.query(models.WechatBinding).filter_by(wx_id=data.wx_id).first()
    if not b:
        return {"reply": "该微信尚未绑定。"}
    _, err = confirmation.resolve(db, b.user_id, data.confirm_id, approve=False)
    return {"reply": err if err else "已取消该操作。"}
