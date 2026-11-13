"""微信网关抽象：业务层只依赖此接口，通道可插拔。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class WeChatMessage:
    msg_id: str
    user_id: str            # 微信原始 ID（用户绑定键）
    sender_name: str
    content: str
    msg_type: str = "text"
    raw: dict = field(default_factory=dict)


class WeChatGateway(ABC):
    @abstractmethod
    def send_text(self, user_id: str, text: str) -> bool:
        """向指定微信用户发送文本。"""

    def send_card(self, user_id: str, title: str, body: str) -> bool:
        """发送卡片（默认退化为标题+正文纯文本）。"""
        return self.send_text(user_id, f"{title}\n{'-' * 24}\n{body}")
