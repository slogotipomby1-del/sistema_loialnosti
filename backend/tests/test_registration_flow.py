import pytest


@pytest.mark.django_db
def test_register_participant_creates_referral_link():
    from apps.bot.services import register_participant
    from apps.referrals.models import ReferralLink

    participant = register_participant(
        telegram_id="1002",
        full_name="Petr Petrov",
        phone="+375299998877",
        consent_accepted=True,
    )

    assert ReferralLink.objects.filter(participant=participant).exists()


@pytest.mark.django_db
def test_registered_participant_has_data_needed_for_member_menu():
    from apps.bot.services import register_participant
    from apps.referrals.models import ReferralLink

    participant = register_participant(
        telegram_id="1005",
        full_name="Sergey Kozlov",
        phone="+375294444444",
        consent_accepted=True,
    )

    link = ReferralLink.objects.get(participant=participant)

    assert participant.full_name == "Sergey Kozlov"
    assert participant.company == ""
    assert participant.position == ""
    assert participant.is_primary_contact is False
    assert link.code
