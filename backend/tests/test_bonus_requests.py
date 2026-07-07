from decimal import Decimal

import pytest


@pytest.mark.django_db
def test_member_can_create_bonus_spend_request():
    from apps.bot.services import create_bonus_spend_request
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="1004",
        full_name="Anna Sidorova",
        phone="+375293333333",
        consent_accepted=True,
    )

    request = create_bonus_spend_request(participant=participant, amount=Decimal("50.00"))

    assert request.status == "pending"
    assert request.amount == Decimal("50.00")
