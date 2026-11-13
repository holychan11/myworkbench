"""本地控制台通道：无真实微信时用于端到端测试。
「发送」的内容进入内存 outbox，由 /gateway/outbox 轮询读取，模拟手机端。
"""
import threading
from datetime import datetime

from .base import WeChatGateway


class ConsoleGateway(WeChatGateway):
    def __init__(self):
        self.outbox: list[dict] = []
        self._lock = threading.Lock()

    def send_text(self, user_id: str, text: str) -> bool:
        with self._lock:
            self.outbox.append({
                "wx_id": user_id, "text": text,
                "ts": datetime.now().isoformat(timespec="seconds")})
        return True

    def send_card(self, user_id: str, title: str, body: str) -> bool:
        return self.send_text(user_id, f"{title}\n{'-' * 24}\n{body}")

    def drain(self, wx_id: str | None = None) -> list[dict]:
        """取出（并清空）待投递消息。"""
        with self._lock:
            if wx_id is None:
                out, self.outbox = self.outbox, []
            else:
                out = [m for m in self.outbox if m["wx_id"] == wx_id]
                self.outbox = [m for m in self.outbox if m["wx_id"] != wx_id]
            return out
