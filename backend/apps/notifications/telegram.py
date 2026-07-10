import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def send_admin_notification(text: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not bot_token or not admin_chat_id:
        return

    payload = urlencode(
        {
            "chat_id": admin_chat_id,
            "text": text,
        }
    ).encode()
    request = Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=payload,
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
        if not data.get("ok"):
            raise RuntimeError("Failed to send admin notification")
