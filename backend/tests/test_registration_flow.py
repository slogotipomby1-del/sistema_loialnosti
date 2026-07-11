import pytest
from django.core.exceptions import ValidationError


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


@pytest.mark.django_db
def test_primary_contact_requires_company():
    from apps.users.models import Participant

    participant = Participant(
        telegram_id="2001",
        full_name="Olga S",
        phone="+375291234567",
        is_primary_contact=True,
        consent_accepted=True,
    )

    with pytest.raises(ValidationError):
        participant.save()


@pytest.mark.django_db
def test_new_primary_contact_replaces_previous_one_in_same_company():
    from apps.users.models import Participant

    first = Participant.objects.create(
        telegram_id="2002",
        full_name="First Contact",
        phone="+375291111111",
        company="ООО Тест",
        is_primary_contact=True,
        consent_accepted=True,
    )
    second = Participant.objects.create(
        telegram_id="2003",
        full_name="Second Contact",
        phone="+375292222222",
        company="ООО Тест",
        is_primary_contact=False,
        consent_accepted=True,
    )

    second.is_primary_contact = True
    second.save()
    first.refresh_from_db()
    second.refresh_from_db()

    assert first.is_primary_contact is False
    assert second.is_primary_contact is True
