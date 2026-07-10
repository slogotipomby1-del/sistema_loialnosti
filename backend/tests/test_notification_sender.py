from io import BytesIO


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_send_admin_notification_skips_without_env(monkeypatch):
    from apps.notifications.telegram import send_admin_notification

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_ADMIN_CHAT_ID", raising=False)

    send_admin_notification("hello")


def test_send_admin_notification_posts_to_telegram(monkeypatch):
    from apps.notifications.telegram import send_admin_notification

    called = {}

    def fake_urlopen(request, timeout=10):
        called["url"] = request.full_url
        called["timeout"] = timeout
        return FakeResponse(b'{"ok": true, "result": {"message_id": 1}}')

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-123")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "999")
    monkeypatch.setattr("apps.notifications.telegram.urlopen", fake_urlopen)

    send_admin_notification("hello")

    assert "token-123" in called["url"]
    assert called["timeout"] == 10
