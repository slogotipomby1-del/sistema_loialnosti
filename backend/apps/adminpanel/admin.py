from django.contrib import admin
from decimal import Decimal

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.common.choices import (
    LEAD_STATUS_BONUS_CONFIRMED,
    LEAD_STATUS_IN_PROGRESS,
    LEAD_STATUS_ORDERED,
    LEAD_STATUS_REJECTED,
    SPEND_REQUEST_STATUS_APPROVED,
    SPEND_REQUEST_STATUS_PENDING,
    SPEND_REQUEST_STATUS_REJECTED,
    get_lead_status_label,
    get_spend_request_status_label,
)
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant

admin.site.site_header = "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043b\u043e\u044f\u043b\u044c\u043d\u043e\u0441\u0442\u0438"
admin.site.site_title = "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043b\u043e\u044f\u043b\u044c\u043d\u043e\u0441\u0442\u0438"
admin.site.index_title = "\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u044f\u0432\u043a\u0430\u043c\u0438 \u0438 \u0431\u043e\u043d\u0443\u0441\u0430\u043c\u0438"
admin.site.index_template = "adminpanel/index.html"
admin.site.empty_value_display = "—"


class ReferralLeadSourceFilter(admin.SimpleListFilter):
    title = "Тип заявки"
    parameter_name = "lead_source"

    def lookups(self, request, model_admin):
        return (
            ("self", "Своя заявка"),
            ("referral", "Реферал"),
        )

    def queryset(self, request, queryset):
        if self.value() == "self":
            return queryset.filter(referral_link__isnull=True)
        if self.value() == "referral":
            return queryset.filter(referral_link__isnull=False)
        return queryset


class HasAdminCommentFilter(admin.SimpleListFilter):
    title = "Комментарий администратора"
    parameter_name = "has_admin_comment"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Есть комментарий"),
            ("no", "Без комментария"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(admin_comment="")
        if self.value() == "no":
            return queryset.filter(admin_comment="")
        return queryset


class HasCommentFilter(admin.SimpleListFilter):
    title = "Комментарий"
    parameter_name = "has_comment"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Есть комментарий"),
            ("no", "Без комментария"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(comment="")
        if self.value() == "no":
            return queryset.filter(comment="")
        return queryset


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
class ParticipantAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "position",
        "is_primary_contact",
        "bonus_balance",
        "invited_leads_count",
        "spend_requests_count",
        "phone",
        "telegram_id",
        "consent_accepted",
        "created_at",
    )
    search_fields = ("full_name", "company", "position", "phone", "telegram_id")
    list_filter = ("consent_accepted", "is_primary_contact", "created_at")
    list_per_page = 25
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "bonus_balance", "invited_leads_count", "spend_requests_count")
    fieldsets = (
        ("Участник", {"fields": ("full_name", "phone", "telegram_id")}),
        ("Компания", {"fields": ("company", "position", "is_primary_contact")}),
        ("Программа", {"fields": ("consent_accepted", "bonus_balance", "invited_leads_count", "spend_requests_count", "created_at")}),
    )

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if obj:
            context["admin_client_card"] = {
                "title": "Карточка участника",
                "items": (
                    ("Участник", obj.full_name or "Не указан"),
                    ("Компания", obj.company or "Не указана"),
                    ("Должность", obj.position or "Не указана"),
                    ("Основной контакт", "Да" if obj.is_primary_contact else "Нет"),
                    ("Телефон", obj.phone or "Не указан"),
                    ("Доступно бонусов", self.bonus_balance(obj)),
                    ("Приглашённых клиентов", self.invited_leads_count(obj)),
                    ("Запросов на списание", self.spend_requests_count(obj)),
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

    @admin.display(description="Бонусы")
    def bonus_balance(self, obj: Participant) -> Decimal:
        accrued = BonusLedgerEntry.objects.filter(participant=obj).values_list("amount", flat=True)
        spent = BonusSpendRequest.objects.filter(
            participant=obj,
            status=SPEND_REQUEST_STATUS_PENDING,
        ).values_list("amount", flat=True)
        return sum(accrued, Decimal("0.00")) - sum(spent, Decimal("0.00"))

    @admin.display(description="Приглашено")
    def invited_leads_count(self, obj: Participant) -> int:
        referral_link = getattr(obj, "referral_link", None)
        if not referral_link:
            return 0
        return (
            ReferralLead.objects.filter(referral_link=referral_link)
            .exclude(client_name=obj.full_name, client_phone=obj.phone)
            .count()
        )

    @admin.display(description="Списания")
    def spend_requests_count(self, obj: Participant) -> int:
        return BonusSpendRequest.objects.filter(participant=obj).count()


@admin.register(ReferralLead)
class ReferralLeadAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = (
        "lead_type_label",
        "client_company",
        "client_name",
        "client_phone",
        "referrer_name",
        "referrer_company",
        "status_label",
        "created_at",
    )
    search_fields = ("client_company", "client_name", "client_phone", "referral_link__participant__full_name")
    list_filter = ("status", "created_at", ReferralLeadSourceFilter, HasAdminCommentFilter)
    autocomplete_fields = ("referral_link",)
    list_select_related = ("referral_link__participant",)
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ("mark_as_in_progress", "mark_as_ordered", "mark_as_bonus_confirmed", "mark_as_rejected")
    readonly_fields = ("lead_type_label", "referrer_name", "referrer_company", "created_at")
    fieldsets = (
        ("Клиент", {"fields": ("client_company", "client_name", "client_phone")}),
        ("Источник", {"fields": ("lead_type_label", "referral_link", "referrer_name", "referrer_company")}),
        ("Обработка", {"fields": ("status", "admin_comment", "created_at")}),
    )
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
                    ("Тип заявки", self.lead_type_label(obj)),
                    ("Клиент", obj.client_name or "Не указан"),
                    ("Компания", obj.client_company or "Не указана"),
                    ("Телефон", obj.client_phone or "Не указан"),
                    ("Кто пригласил", self.referrer_name(obj)),
                    ("Компания пригласившего", self.referrer_company(obj)),
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

    @admin.display(description="Тип")
    def lead_type_label(self, obj: ReferralLead) -> str:
        return "Своя заявка" if not obj.referral_link else "Реферал"

    @admin.display(description="Компания пригласившего")
    def referrer_company(self, obj: ReferralLead) -> str:
        if not obj.referral_link:
            return "—"
        return obj.referral_link.participant.company or "Не указана"

    @admin.display(description="Статус")
    def status_label(self, obj: ReferralLead) -> str:
        return get_lead_status_label(obj.status)

    @admin.action(description="Перевести в статус «В работе»")
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status=LEAD_STATUS_IN_PROGRESS)

    @admin.action(description="Перевести в статус «Ожидает подтверждения»")
    def mark_as_ordered(self, request, queryset):
        queryset.update(status=LEAD_STATUS_ORDERED)

    @admin.action(description="Перевести в статус «Бонус начислен»")
    def mark_as_bonus_confirmed(self, request, queryset):
        queryset.update(status=LEAD_STATUS_BONUS_CONFIRMED)

    @admin.action(description="Перевести в статус «Отклонена»")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status=LEAD_STATUS_REJECTED)


@admin.register(ReferralLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "participant")
    search_fields = ("code", "participant__full_name", "participant__phone")
    autocomplete_fields = ("participant",)
    list_select_related = ("participant",)


@admin.register(BonusLedgerEntry)
class BonusLedgerEntryAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = ("participant", "amount", "reason", "lead", "created_at")
    search_fields = ("participant__full_name", "reason", "lead__client_name")
    list_filter = ("created_at",)
    autocomplete_fields = ("participant", "lead")
    list_select_related = ("participant", "lead")
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Начисление", {"fields": ("participant", "amount", "reason", "lead", "created_at")}),
    )
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
    list_display = ("participant", "participant_company", "participant_phone", "comment", "amount", "status_label", "created_at")
    search_fields = ("participant__full_name", "participant__company", "participant__phone", "comment")
    list_filter = ("status", "created_at", HasCommentFilter)
    autocomplete_fields = ("participant",)
    list_select_related = ("participant",)
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ("mark_as_approved", "mark_as_rejected")
    readonly_fields = ("participant_phone", "participant_company", "created_at")
    fieldsets = (
        ("Участник", {"fields": ("participant", "participant_company", "participant_phone")}),
        ("Запрос", {"fields": ("comment", "amount", "status", "created_at")}),
    )
    memo_title = "Проверка списания бонусов"
    memo_intro = "Списание подтверждается вручную и только по правилам программы."
    memo_items = (
        "Проверьте, хватает ли участнику бонусов на списание.",
        "Проверьте, что бонусы не используются вместе со скидками или спецусловиями.",
        "Проверьте, что списание не относится к тендерному или низкомаржинальному заказу.",
        "Допустимо использовать бонусы на подарок, доставку, нанесение или часть следующего заказа.",
    )
    memo_note = "Если запрос спорный, оставьте комментарий и принимайте решение вручную."

    @admin.display(description="Телефон")
    def participant_phone(self, obj: BonusSpendRequest) -> str:
        return obj.participant.phone

    @admin.display(description="Компания")
    def participant_company(self, obj: BonusSpendRequest) -> str:
        return obj.participant.company or "Не указана"

    @admin.display(description="Статус")
    def status_label(self, obj: BonusSpendRequest) -> str:
        return get_spend_request_status_label(obj.status)

    @admin.action(description="Перевести в статус «Подтверждена»")
    def mark_as_approved(self, request, queryset):
        queryset.update(status=SPEND_REQUEST_STATUS_APPROVED)

    @admin.action(description="Перевести в статус «Отклонена»")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status=SPEND_REQUEST_STATUS_REJECTED)
