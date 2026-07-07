from django.contrib.admin.sites import site

from apps.bonuses.models import BonusSpendRequest
from apps.referrals.models import ReferralLead, ReferralLink


def test_referral_lead_admin_has_main_columns():
    admin_instance = site._registry[ReferralLead]

    assert admin_instance.list_display == (
        "client_name",
        "client_phone",
        "referrer_name",
        "status",
        "created_at",
    )


def test_bonus_spend_request_admin_has_main_columns():
    admin_instance = site._registry[BonusSpendRequest]

    assert admin_instance.list_display == (
        "participant",
        "amount",
        "status",
        "created_at",
    )


def test_referral_link_admin_is_registered_for_autocomplete():
    admin_instance = site._registry[ReferralLink]

    assert admin_instance.search_fields == ("code", "participant__full_name", "participant__phone")
