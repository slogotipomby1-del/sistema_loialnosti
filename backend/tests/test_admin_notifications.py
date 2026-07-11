import pytest


@pytest.mark.django_db
def test_lead_creation_triggers_admin_notification(monkeypatch):
    from apps.bot.services import create_referral_lead
    from apps.referrals.models import ReferralLink
    from apps.users.models import Participant

    sent = {}

    def fake_send_admin_notification(text: str):
        sent["text"] = text

    monkeypatch.setattr("apps.notifications.telegram.send_admin_notification", fake_send_admin_notification)

    participant = Participant.objects.create(
        telegram_id="1003",
        full_name="Olga Petrova",
        phone="+375291111111",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="ref-1003", participant=participant)

    lead = create_referral_lead(
        referral_code=link.code,
        client_name="Ivan Ivanov",
        client_phone="+375292222222",
        client_company="OOO New Client",
    )

    assert lead.referral_link == link
    assert "OOO New Client" in sent["text"]
    assert "Ivan Ivanov" in sent["text"]
