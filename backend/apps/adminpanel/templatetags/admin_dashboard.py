from django import template
from django.urls import reverse

from apps.bonuses.models import BonusSpendRequest
from apps.common.choices import LEAD_STATUS_NEW, SPEND_REQUEST_STATUS_PENDING
from apps.referrals.models import ReferralLead

register = template.Library()


@register.simple_tag
def admin_dashboard_cards():
    new_leads_count = ReferralLead.objects.filter(status=LEAD_STATUS_NEW).count()
    self_leads_count = ReferralLead.objects.filter(referral_link__isnull=True).count()
    pending_spend_count = BonusSpendRequest.objects.filter(
        status=SPEND_REQUEST_STATUS_PENDING
    ).count()
    disputed_count = ReferralLead.objects.exclude(admin_comment="").count()

    return (
        {
            "title": "Новые заявки",
            "count": new_leads_count,
            "hint": "Новые клиенты и новые обращения участников.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?status={LEAD_STATUS_NEW}",
        },
        {
            "title": "Свои заявки",
            "count": self_leads_count,
            "hint": "Заявки участников для своей компании.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?lead_source=self",
        },
        {
            "title": "Списания на рассмотрении",
            "count": pending_spend_count,
            "hint": "Подарки и списания, которые ждут решения.",
            "url": f"{reverse('admin:bonuses_bonusspendrequest_changelist')}?status={SPEND_REQUEST_STATUS_PENDING}",
        },
        {
            "title": "Спорные случаи",
            "count": disputed_count,
            "hint": "Заявки с комментарием администратора.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?has_admin_comment=yes",
        },
    )
