from django import template
from django.urls import reverse

from apps.bonuses.models import BonusSpendRequest
from apps.bonuses.services import get_expiring_bonus_preview, get_upcoming_expiration_warning_preview
from apps.common.choices import LEAD_STATUS_NEW, LEAD_STATUS_ORDERED, SPEND_REQUEST_STATUS_PENDING
from apps.referrals.models import ReferralLead
from apps.users.models import Participant

register = template.Library()


@register.simple_tag
def admin_dashboard_cards():
    new_leads_count = ReferralLead.objects.filter(status=LEAD_STATUS_NEW).count()
    self_leads_count = ReferralLead.objects.filter(referral_link__isnull=True).count()
    ordered_leads_count = ReferralLead.objects.filter(status=LEAD_STATUS_ORDERED).count()
    pending_spend_count = BonusSpendRequest.objects.filter(
        status=SPEND_REQUEST_STATUS_PENDING
    ).count()
    upcoming_expiration_count = len(get_upcoming_expiration_warning_preview())
    expired_bonus_count = len(get_expiring_bonus_preview())
    disputed_count = ReferralLead.objects.exclude(admin_comment="").count()
    participants_without_company_count = Participant.objects.filter(company="").count()

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
            "title": "Ждут подтверждения",
            "count": ordered_leads_count,
            "hint": "Заказы состоялись, но бонус ещё не подтверждён.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?status={LEAD_STATUS_ORDERED}",
        },
        {
            "title": "Списания на рассмотрении",
            "count": pending_spend_count,
            "hint": "Подарки и списания, которые ждут решения.",
            "url": f"{reverse('admin:bonuses_bonusspendrequest_changelist')}?status={SPEND_REQUEST_STATUS_PENDING}",
        },
        {
            "title": "Скоро сгорят",
            "count": upcoming_expiration_count,
            "hint": "Бонусы, по которым скоро нужно отправлять предупреждение участнику.",
            "url": f"{reverse('admin:bonuses_bonusledgerentry_changelist')}?bonus_expiration_state=warning",
        },
        {
            "title": "Уже просрочены",
            "count": expired_bonus_count,
            "hint": "Бонусы с истёкшим сроком, которые готовы к dry-run или ручной проверке.",
            "url": f"{reverse('admin:bonuses_bonusledgerentry_changelist')}?bonus_expiration_state=expired",
        },
        {
            "title": "Спорные случаи",
            "count": disputed_count,
            "hint": "Заявки с комментарием администратора.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?has_admin_comment=yes",
        },
        {
            "title": "Профили без компании",
            "count": participants_without_company_count,
            "hint": "Участники, у которых ещё не заполнена компания.",
            "url": f"{reverse('admin:users_participant_changelist')}?company__exact=",
        },
    )


@register.simple_tag
def admin_dashboard_priority_items():
    return (
        {
            "title": "Новые заявки",
            "text": "Сначала проверьте новых клиентов и дубли по телефону или компании.",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?status={LEAD_STATUS_NEW}",
        },
        {
            "title": "Бонусы к подтверждению",
            "text": "Отдельно посмотрите заказы со статусом «Ожидает подтверждения».",
            "url": f"{reverse('admin:referrals_referrallead_changelist')}?status={LEAD_STATUS_ORDERED}",
        },
        {
            "title": "Списания бонусов",
            "text": "Проверьте подарки и списания, которые ждут вашего решения.",
            "url": f"{reverse('admin:bonuses_bonusspendrequest_changelist')}?status={SPEND_REQUEST_STATUS_PENDING}",
        },
        {
            "title": "Сгорание бонусов",
            "text": "Проверьте, не появились ли бонусы, по которым нужно отправить предупреждение или запустить dry-run.",
            "url": f"{reverse('admin:bonuses_bonusledgerentry_changelist')}?bonus_expiration_state=warning",
        },
    )


@register.simple_tag
def admin_dashboard_quick_links():
    return (
        {
            "title": "Открыть все заявки",
            "url": reverse("admin:referrals_referrallead_changelist"),
        },
        {
            "title": "Открыть списания бонусов",
            "url": reverse("admin:bonuses_bonusspendrequest_changelist"),
        },
        {
            "title": "Открыть операции по бонусам",
            "url": f"{reverse('admin:bonuses_bonusledgerentry_changelist')}?bonus_expiration_state=warning",
        },
        {
            "title": "Открыть участников",
            "url": reverse("admin:users_participant_changelist"),
        },
    )
