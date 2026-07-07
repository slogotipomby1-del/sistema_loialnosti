from django.contrib import admin

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant

admin.site.site_header = "Админка программы лояльности"
admin.site.site_title = "Админка программы лояльности"
admin.site.index_title = "Управление заявками и бонусами"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "telegram_id", "consent_accepted", "created_at")
    search_fields = ("full_name", "phone", "telegram_id")
    list_filter = ("consent_accepted", "created_at")


@admin.register(ReferralLead)
class ReferralLeadAdmin(admin.ModelAdmin):
    list_display = ("client_name", "client_phone", "referrer_name", "status", "created_at")
    search_fields = ("client_name", "client_phone", "referral_link__participant__full_name")
    list_filter = ("status", "created_at")
    autocomplete_fields = ("referral_link",)

    @admin.display(description="Кто пригласил")
    def referrer_name(self, obj: ReferralLead) -> str:
        if not obj.referral_link:
            return "Без реферала"
        return obj.referral_link.participant.full_name


@admin.register(ReferralLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "participant")
    search_fields = ("code", "participant__full_name", "participant__phone")
    autocomplete_fields = ("participant",)


@admin.register(BonusLedgerEntry)
class BonusLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("participant", "amount", "reason", "lead", "created_at")
    search_fields = ("participant__full_name", "reason", "lead__client_name")
    list_filter = ("created_at",)
    autocomplete_fields = ("participant", "lead")


@admin.register(BonusSpendRequest)
class BonusSpendRequestAdmin(admin.ModelAdmin):
    list_display = ("participant", "amount", "status", "created_at")
    search_fields = ("participant__full_name", "participant__phone")
    list_filter = ("status", "created_at")
    autocomplete_fields = ("participant",)
