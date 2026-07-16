import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def send_telegram_message(*, chat_id: str, text: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = (chat_id or "").strip()
    if not bot_token or not chat_id:
        return

    payload = urlencode(
        {
            "chat_id": chat_id,
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


def send_admin_notification(text: str) -> None:
    admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not admin_chat_id:
        return

    send_telegram_message(chat_id=admin_chat_id, text=text)
