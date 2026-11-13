"""Pydantic 请求/响应模型。"""
from typing import Optional

from pydantic import BaseModel, Field


# ---------- 认证 ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: str


class UserOut(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool


# ---------- 模型配置 ----------
class ModelIn(BaseModel):
    display_name: str
    provider: str = "custom"
    base_url: str
    api_key: str
    default_model: str
    temperature: float = 0.7
    is_default: bool = False


class ModelOut(BaseModel):
    id: str
    display_name: str
    provider: str
    base_url: str
    api_key_masked: str
    default_model: str
    temperature: float
    is_default: bool
    enabled: bool


class ModelTestOut(BaseModel):
    ok: bool
    reply: str = ""


# ---------- 微信绑定 ----------
class BindCodeOut(BaseModel):
    bind_code: str
    expires_in: int = 600


class BindIn(BaseModel):
    code: str
    wx_id: str
    wx_nick: str = ""


class BindOut(BaseModel):
    bound: bool
    wx_id: Optional[str] = None


# ---------- 网关模拟 / 确认 ----------
class SimulateIn(BaseModel):
    wx_id: str
    text: str
    nick: str = ""


class MessageOut(BaseModel):
    wx_id: str
    text: str
    ts: str


class ConfirmIn(BaseModel):
    wx_id: str
    confirm_id: str


# ---------- A股 ----------
class StockRunOut(BaseModel):
    strategy_id: str
    trade_date: str
    report: str


class PrefsIn(BaseModel):
    premarket_enabled: bool
    premarket_strategy: str = "premarket_momentum"
    risk_level: str = "medium"


class ReportOut(BaseModel):
    id: int
    strategy_id: str
    trade_date: str
    picks: list
    created_at: str
