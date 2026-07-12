from apps.common.choices import (
    get_lead_status_label,
    get_spend_request_status_label,
)


def test_get_lead_status_label_returns_human_text():
    assert get_lead_status_label("ordered") == "Ожидает подтверждения"
    assert get_lead_status_label("bonus_confirmed") == "Бонус начислен"


def test_get_spend_request_status_label_returns_human_text():
    assert get_spend_request_status_label("pending") == "На рассмотрении"
    assert get_spend_request_status_label("approved") == "Подтверждена"
