"""WeChatFerry 通道（Windows 个人号 Hook，可选安装 wcferry）。"""
from .base import WeChatGateway


class WcfGateway(WeChatGateway):
    def __init__(self, host: str = "127.0.0.1", port: int = 10086):
        try:
            import wcferry  # noqa: F401
        except ImportError as e:
            raise RuntimeError("未安装 wcferry，请先 `pip install wcferry`") from e
        self._wcf = wcferry.Wcf(host=host, port=port)

    def send_text(self, user_id: str, text: str) -> bool:
        return self._wcf.send_text(text, receiver=user_id) > 0
