from django.contrib import admin

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import get_lead_status_label
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant

admin.site.site_header = "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043b\u043e\u044f\u043b\u044c\u043d\u043e\u0441\u0442\u0438"
admin.site.site_title = "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043b\u043e\u044f\u043b\u044c\u043d\u043e\u0441\u0442\u0438"
admin.site.index_title = "\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u044f\u0432\u043a\u0430\u043c\u0438 \u0438 \u0431\u043e\u043d\u0443\u0441\u0430\u043c\u0438"
admin.site.index_template = "adminpanel/index.html"


class AdminMemoMixin:
    change_form_template = "adminpanel/change_form.html"
    memo_title = ""
    memo_intro = ""
    memo_items: tuple[str, ...] = ()
    memo_note = ""

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        context["admin_memo"] = {
            "title": self.memo_title,
            "intro": self.memo_intro,
            "items": self.memo_items,
            "note": self.memo_note,
        }
        return super().render_change_form(
            request,
            context,
            add=add,
            change=change,
            form_url=form_url,
            obj=obj,
        )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "position", "is_primary_contact", "phone", "telegram_id", "consent_accepted", "created_at")
    search_fields = ("full_name", "company", "position", "phone", "telegram_id")
    list_filter = ("consent_accepted", "is_primary_contact", "created_at")


@admin.register(ReferralLead)
class ReferralLeadAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = ("client_company", "client_name", "client_phone", "referrer_name", "status", "created_at")
    search_fields = ("client_company", "client_name", "client_phone", "referral_link__participant__full_name")
    list_filter = ("status", "created_at")
    autocomplete_fields = ("referral_link",)
    memo_title = "Проверка реферальной заявки"
    memo_intro = "Перед подтверждением проверьте, что клиент действительно подходит под правила программы."
    memo_items = (
        "Проверьте, новый ли это клиент, и нет ли дубля по телефону, компании или CRM.",
        "Проверьте, не является ли это саморефералом или своей же компанией через другой аккаунт.",
        "Если одного клиента привели два участника, засчитывается первая ссылка.",
        "Если у компании уже были успешные завершённые заказы, заявка не считается новой рекомендацией.",
    )
    memo_note = "После проверки выберите статус заявки и зафиксируйте комментарий, если есть спорный случай."

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if obj:
            context["admin_client_card"] = {
                "title": "Карточка клиента",
                "items": (
                    ("Клиент", obj.client_name or "Не указан"),
                    ("Компания", obj.client_company or "Не указана"),
                    ("Телефон", obj.client_phone or "Не указан"),
                    ("Кто пригласил", self.referrer_name(obj)),
                    ("Статус заявки", get_lead_status_label(obj.status)),
                    ("Комментарий администратора", obj.admin_comment or "Комментарий пока не добавлен"),
                ),
            }
        return super().render_change_form(
            request,
            context,
            add=add,
            change=change,
            form_url=form_url,
            obj=obj,
        )

    @admin.display(description="\u041a\u0442\u043e \u043f\u0440\u0438\u0433\u043b\u0430\u0441\u0438\u043b")
    def referrer_name(self, obj: ReferralLead) -> str:
        if not obj.referral_link:
            return "\u0411\u0435\u0437 \u0440\u0435\u0444\u0435\u0440\u0430\u043b\u0430"
        return obj.referral_link.participant.full_name


@admin.register(ReferralLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "participant")
    search_fields = ("code", "participant__full_name", "participant__phone")
    autocomplete_fields = ("participant",)


@admin.register(BonusLedgerEntry)
class BonusLedgerEntryAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = ("participant", "amount", "reason", "lead", "created_at")
    search_fields = ("participant__full_name", "reason", "lead__client_name")
    list_filter = ("created_at",)
    autocomplete_fields = ("participant", "lead")
    memo_title = "Проверка начисления бонусов"
    memo_intro = "Начисление делается только после ручной проверки условий сделки."
    memo_items = (
        "Проверьте, что заказ оплачен и отгружен.",
        "Проверьте сумму заказа: бонусы не начисляются по заказам ниже 2000 BYN.",
        "Проверьте, что заказ не тендерный, не низкомаржинальный и без скидки или спецусловий.",
        "Если заказ компании делает несколько участников, бонус за заказ компании идёт основному контакту.",
    )
    memo_note = "Главный принцип: сначала проверить экономику сделки, потом начислять бонус."


@admin.register(BonusSpendRequest)
class BonusSpendRequestAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = ("participant", "comment", "amount", "status", "created_at")
    search_fields = ("participant__full_name", "participant__phone", "comment")
    list_filter = ("status", "created_at")
    autocomplete_fields = ("participant",)
    memo_title = "Проверка списания бонусов"
    memo_intro = "Списание подтверждается вручную и только по правилам программы."
    memo_items = (
        "Проверьте, хватает ли участнику бонусов на списание.",
        "Проверьте, что бонусы не используются вместе со скидками или спецусловиями.",
        "Проверьте, что списание не относится к тендерному или низкомаржинальному заказу.",
        "Допустимо использовать бонусы на подарок, доставку, нанесение или часть следующего заказа.",
    )
    memo_note = "Если запрос спорный, оставьте комментарий и принимайте решение вручную."
