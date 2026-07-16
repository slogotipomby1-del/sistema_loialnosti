def test_send_telegram_message_skips_without_token(monkeypatch):
    from apps.notifications.telegram import send_telegram_message

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    send_telegram_message(chat_id="123", text="hello")


def test_send_telegram_message_posts_to_telegram(monkeypatch):
    from apps.notifications.telegram import send_telegram_message

    called = {}

    class FakeResponse:
        def read(self):
            return b'{"ok": true, "result": {"message_id": 1}}'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout=10):
        called["url"] = request.full_url
        called["timeout"] = timeout
        called["data"] = request.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-xyz")
    monkeypatch.setattr("apps.notifications.telegram.urlopen", fake_urlopen)

    send_telegram_message(chat_id="555", text="hello")

    assert "token-xyz" in called["url"]
    assert called["timeout"] == 10
    assert "chat_id=555" in called["data"]
