import pytest


@pytest.mark.django_db
def test_lead_created_from_referral_keeps_referrer_relation():
    from apps.users.models import Participant
    from apps.referrals.models import ReferralLead, ReferralLink

    participant = Participant.objects.create(
        telegram_id="1001",
        full_name="Ivan Ivanov",
        phone="+375291112233",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="abc123", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_name="OOO Client",
        client_phone="+375291234567",
        client_company="OOO Client",
        client_position="Маркетолог",
        client_email="client@example.com",
        product_interest="Welcome pack",
        quantity="200",
        budget="до 5000 BYN",
        deadline="2 недели",
        status="new",
    )

    assert lead.referral_link.participant == participant
    assert lead.client_company == "OOO Client"
    assert lead.client_email == "client@example.com"
