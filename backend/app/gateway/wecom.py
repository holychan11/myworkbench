"""企业微信应用通道（官方 API，合规首选）。"""
from .base import WeChatGateway


class WeComGateway(WeChatGateway):
    def __init__(self, corp_id: str, agent_id: str, secret: str):
        self._corp_id = corp_id
        self._agent_id = agent_id
        self._secret = secret

    def _token(self) -> str:
        import httpx
        r = httpx.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
            params={"corpid": self._corp_id, "corpsecret": self._secret},
            timeout=10)
        return r.json().get("access_token", "")

    def send_text(self, user_id: str, text: str) -> bool:
        import httpx
        tok = self._token()
        if not tok:
            return False
        r = httpx.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send",
            params={"access_token": tok},
            json={"touser": user_id, "msgtype": "text",
                  "agentid": int(self._agent_id), "text": {"content": text}},
            timeout=10)
        return r.json().get("errcode") == 0
