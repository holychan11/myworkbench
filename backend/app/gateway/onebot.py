"""OneBot 11 适配器（QQ 通道）。

通过 NapCat / LLOneBot 等 OneBot 框架接入 QQ：
- 收消息：框架把事件 HTTP 上报到本服务的 /onebot/event
- 发消息：调用框架的 HTTP API send_private_msg

绑定键 = 发送者 QQ 号。
"""
import httpx

from .base import WeChatGateway, WeChatMessage


def parse_text(message) -> str:
    """OneBot message 可能是字符串(CQ码)或消息段数组，统一提取纯文本。"""
    if isinstance(message, str):
        return message
    if isinstance(message, list):
        parts = []
        for seg in message:
            if isinstance(seg, dict) and seg.get("type") == "text":
                parts.append((seg.get("data") or {}).get("text", ""))
        return "".join(parts)
    return str(message)


class OneBotAdapter(WeChatGateway):
    def __init__(self, http_url: str):
        self.http_url = http_url.rstrip("/")

    def send_text(self, user_id: str, text: str) -> bool:
        try:
            r = httpx.post(
                f"{self.http_url}/send_private_msg",
                json={"user_id": int(user_id), "message": text},
                timeout=10)
            return r.status_code < 400 and r.json().get("status") == "ok"
        except Exception:  # noqa: BLE001
            return False

    def send_card(self, user_id: str, title: str, body: str) -> bool:
        return self.send_text(user_id, f"{title}\n{'-' * 24}\n{body}")
