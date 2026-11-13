"""网关工厂：按 GATEWAY_TYPE 选择通道，默认 console（本地测试）。"""
from ..config import settings
from .base import WeChatGateway
from .console import ConsoleGateway


def create_gateway() -> WeChatGateway:
    t = settings.GATEWAY_TYPE.lower()
    if t == "wecom":
        from .wecom import WeComGateway
        return WeComGateway(settings.WECOM_CORP_ID, settings.WECOM_AGENT_ID,
                            settings.WECOM_SECRET)
    if t == "wcf":
        from .wcf import WcfGateway
        return WcfGateway(settings.WCF_HOST, settings.WCF_PORT)
    if t == "onebot":
        from .onebot import OneBotAdapter
        return OneBotAdapter(settings.ONE_BOT_HTTP_URL)
    return ConsoleGateway()
