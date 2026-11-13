"""ORM 模型。所有用户数据按 user_id 分区，实现多租户隔离。"""
import uuid
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship

from .database import Base


def _uid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(String(32), primary_key=True, default=_uid)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(16), default="user")          # user | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)

    binding = relationship("WechatBinding", back_populates="user",
                           uselist=False, cascade="all, delete-orphan")
    models = relationship("UserModel", back_populates="user",
                          cascade="all, delete-orphan")


class WechatBinding(Base):
    __tablename__ = "wechat_bindings"
    user_id = Column(String(32), ForeignKey("users.id"), primary_key=True)
    wx_id = Column(String(128), unique=True, index=True, nullable=False)
    wx_nick = Column(String(128), default="")
    bound_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="binding")


class UserModel(Base):
    """用户配置的 LLM（API Key 存 Fernet 密文）。"""
    __tablename__ = "user_models"
    id = Column(String(32), primary_key=True, default=_uid)
    user_id = Column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    display_name = Column(String(64), nullable=False)
    provider = Column(String(32), nullable=False)
    base_url = Column(String(256), nullable=False)
    api_key_enc = Column(Text, nullable=False)          # Fernet 密文
    default_model = Column(String(128), nullable=False)
    temperature = Column(Float, default=0.7)
    is_default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="models")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(32), primary_key=True, default=_uid)
    user_id = Column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    channel = Column(String(16), default="wechat")       # wechat | web
    messages = Column(Text, default="[]")                # JSON 字符串
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class TaskLog(Base):
    """全量审计：命令执行、二次确认、LLM 调用、报告推送。"""
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    kind = Column(String(32), nullable=False)            # exec | confirm | llm | report
    cmd = Column(Text, default="")
    risk = Column(String(16), default="")                # safe | risky | forbidden
    status = Column(String(16), nullable=False)          # ok | failed | pending | approved | rejected | timed_out
    result = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


class PendingConfirmation(Base):
    """二次确认状态机（SQLite 实现，expires_at 模拟 TTL）。"""
    __tablename__ = "pending_confirmations"
    id = Column(String(32), primary_key=True, default=_uid)
    user_id = Column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    cmd = Column(Text, nullable=False)
    risk = Column(String(16), default="risky")
    status = Column(String(16), default="pending")       # pending | approved | rejected | expired
    created_at = Column(DateTime, default=_now)
    expires_at = Column(DateTime, nullable=False)


class StockReport(Base):
    __tablename__ = "stock_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    strategy_id = Column(String(64), nullable=False)
    trade_date = Column(String(16), nullable=False)
    picks = Column(Text, default="[]")                   # JSON 字符串
    created_at = Column(DateTime, default=_now)


class UserPref(Base):
    __tablename__ = "user_prefs"
    user_id = Column(String(32), ForeignKey("users.id"), primary_key=True)
    premarket_enabled = Column(Boolean, default=False)    # 订阅盘前报告
    premarket_strategy = Column(String(64), default="premarket_momentum")
    risk_level = Column(String(16), default="medium")     # low | medium | high
