"""微信绑定码服务：内存存储 + TTL，一次性使用，防抢占。"""
import threading
import time
import uuid

from sqlalchemy.orm import Session

from .. import models
from ..core.audit import log

BIND_TTL_SECONDS = 600
_store: dict[str, dict] = {}
_lock = threading.Lock()


def issue(user_id: str) -> str:
    code = uuid.uuid4().hex[:8].upper()
    with _lock:
        _store[code] = {"user_id": user_id, "exp": time.time() + BIND_TTL_SECONDS}
    return code


def confirm(db: Session, code: str, wx_id: str, wx_nick: str = ""):
    """用绑定码绑定微信。返回 (user | None, err | None)。"""
    with _lock:
        rec = _store.pop(code, None)
    if not rec or time.time() > rec["exp"]:
        return None, "绑定码无效或已过期，请在 Web 端重新生成"

    # 防抢占：该微信已绑定其他账号则拒绝
    existing = db.query(models.WechatBinding).filter_by(wx_id=wx_id).first()
    if existing and existing.user_id != rec["user_id"]:
        return None, "该微信已绑定其他账号，请先在 Web 端解绑"

    user = db.get(models.User, rec["user_id"])
    if not user:
        return None, "用户不存在"

    binding = db.get(models.WechatBinding, rec["user_id"])
    if binding:
        binding.wx_id = wx_id
        binding.wx_nick = wx_nick or binding.wx_nick
    else:
        db.add(models.WechatBinding(user_id=rec["user_id"], wx_id=wx_id, wx_nick=wx_nick))
    db.commit()
    log(db, rec["user_id"], "bind", cmd=f"bind {wx_id}", status="ok")
    return user, None


def get_binding(db: Session, user_id: str) -> models.WechatBinding | None:
    return db.get(models.WechatBinding, user_id)
