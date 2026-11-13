"""OneBot 11 消息上报端点（QQ 通道收消息）。

NapCat / LLOneBot 把 HTTP 上报地址配置为：
  http://<本机>:8000/onebot/event
"""
from fastapi import APIRouter, Request

from ..database import SessionLocal
from ..gateway.onebot import parse_text

router = APIRouter(tags=["onebot"])


@router.post("/onebot/event")
async def on_event(request: Request):
    try:
        data = await request.json()
    except Exception:  # noqa: BLE001
        return {}

    # 只处理私聊文本消息（个人遥控以私聊为主）
    if data.get("post_type") != "message" or data.get("message_type") != "private":
        return {}
    user_id = str(data.get("user_id", ""))
    if not user_id:
        return {}

    text = parse_text(data.get("message", ""))
    if not text.strip():
        return {}

    db = SessionLocal()
    try:
        reply = request.app.state.dispatcher.dispatch(db, user_id, "", text)
        if reply:
            request.app.state.gateway.send_text(user_id, reply)
    finally:
        db.close()
    return {}
