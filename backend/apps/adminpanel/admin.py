from django.contrib import admin
from decimal import Decimal
import csv
from django.http import HttpResponse
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.bonuses.services import get_expiring_bonus_preview, get_upcoming_expiration_warning_preview
from apps.common.choices import (
    BONUS_ENTRY_TYPE_ACCRUAL,
    BONUS_ENTRY_TYPE_MANUAL_ADJUSTMENT,
    BONUS_ENTRY_TYPE_REVERSAL,
    LEAD_STATUS_BONUS_CONFIRMED,
    LEAD_STATUS_IN_PROGRESS,
    LEAD_STATUS_ORDERED,
    LEAD_STATUS_REJECTED,
    SPEND_REQUEST_STATUS_APPROVED,
    SPEND_REQUEST_STATUS_PENDING,
    SPEND_REQUEST_STATUS_REJECTED,
    get_bonus_entry_type_label,
    get_lead_status_label,
    get_spend_request_status_label,
)
from apps.referrals.models import ReferralLead, ReferralLink
from apps.users.models import Participant
from apps.bot.services import calculate_participant_balance

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


class ReferralLeadDuplicateFilter(admin.SimpleListFilter):
    title = "Дубли"
    parameter_name = "duplicate_state"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Есть возможные дубли"),
            ("clean", "Без дублей"),
            ("phone", "Дубли по телефону"),
            ("company", "Дубли по компании"),
        )

    def queryset(self, request, queryset):
        duplicate_phone_values = (
            queryset.exclude(client_phone="")
            .values("client_phone")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .values("client_phone")
        )
        duplicate_company_values = (
            queryset.exclude(client_company="")
            .values("client_company")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .values("client_company")
        )

        if self.value() == "yes":
            return queryset.filter(
                Q(client_phone__in=duplicate_phone_values) | Q(client_company__in=duplicate_company_values)
            )
        if self.value() == "clean":
            return queryset.exclude(
                Q(client_phone__in=duplicate_phone_values) | Q(client_company__in=duplicate_company_values)
            )
        if self.value() == "phone":
            return queryset.filter(client_phone__in=duplicate_phone_values)
        if self.value() == "company":
            return queryset.filter(client_company__in=duplicate_company_values)
        return queryset


class ParticipantCompanyStateFilter(admin.SimpleListFilter):
    title = "Компания"
    parameter_name = "company_state"

    def lookups(self, request, model_admin):
        return (
            ("with_company", "Есть компания"),
            ("without_company", "Без компании"),
            ("team", "В компании несколько участников"),
            ("without_primary", "В компании нет основного контакта"),
        )

    def queryset(self, request, queryset):
        company_values_with_team = (
            queryset.exclude(company="")
            .values("company")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .values("company")
        )
        company_values_with_primary = (
            queryset.exclude(company="")
            .filter(is_primary_contact=True)
            .values("company")
        )

        if self.value() == "with_company":
            return queryset.exclude(company="")
        if self.value() == "without_company":
            return queryset.filter(company="")
        if self.value() == "team":
            return queryset.filter(company__in=company_values_with_team)
        if self.value() == "without_primary":
            return queryset.exclude(company="").exclude(company__in=company_values_with_primary)
        return queryset


class BonusLedgerExpirationStateFilter(admin.SimpleListFilter):
    title = "Контроль сгорания"
    parameter_name = "bonus_expiration_state"

    def lookups(self, request, model_admin):
        return (
            ("warning", "Скоро сгорят"),
            ("expired", "Уже просрочены"),
        )

    def queryset(self, request, queryset):
        if self.value() == "warning":
            warning_entry_ids = [item.entry.id for item in get_upcoming_expiration_warning_preview()]
            return queryset.filter(id__in=warning_entry_ids)
        if self.value() == "expired":
            expired_entry_ids = [item.entry.id for item in get_expiring_bonus_preview()]
            return queryset.filter(id__in=expired_entry_ids)
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





def build_csv_response(*, filename: str, header: list[str], rows: list[list[str]]) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(header)
    writer.writerows(rows)
    return response


@admin.register(Participant)
class ParticipantAdmin(AdminMemoMixin, admin.ModelAdmin):
    memo_title = "Памятка по участнику"
    memo_intro = "Перед начислением или списанием проверьте, что карточка участника заполнена корректно."
    memo_items = (
        "Проверьте телефон, компанию и должность участника: эти данные нужны для проверки дублей и связи с клиентом.",
        "Если в компании несколько участников, убедитесь, кто является основным контактом.",
        "Перед подтверждением бонусов проверьте, что есть основание: оплаченный заказ, рекомендация или ручная корректировка.",
        "Перед списанием проверьте доступный баланс, назначение подарка или доставки и статус запроса.",
        "Если участник меняет компанию или основной контакт уволился, обновите карточку до начисления новых бонусов.",
        "согласие на обработку персональных данных должно быть получено до работы с участником в программе.",
    )
    memo_note = "Если случай спорный, зафиксируйте решение в комментарии администратора у заявки или бонусной операции."

    list_display = (
        "full_name",
        "company_badge",
        "company_team_size",
        "position",
        "contact_role_badge",
        "bonus_balance_badge",
        "invited_leads_count",
        "spend_requests_count",
        "pending_spend_requests_count",
        "quick_actions",
        "phone",
        "created_at",
    )
    search_fields = ("full_name", "company", "position", "phone", "telegram_id")
    list_filter = ("consent_accepted", "is_primary_contact", "created_at", ParticipantCompanyStateFilter)
    actions = ("export_selected_to_csv",)
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
                    ("Telegram ID", obj.telegram_id or "Не указан"),
                    ("Согласие", "Получено" if obj.consent_accepted else "Не получено"),
                    ("Участников в компании", self.company_team_size(obj)),
                    ("Доступно бонусов", self.bonus_balance(obj)),
                    ("Приглашённых клиентов", self.invited_leads_count(obj)),
                    ("Запросов на списание", self.spend_requests_count(obj)),
                    ("Списаний на рассмотрении", self.pending_spend_requests_count(obj)),
                ),
            }
            context["admin_action_links"] = self.build_participant_action_links(obj)
            context["admin_history_title"] = "Операционный контекст участника"
            context["admin_history_intro"] = "Баланс, заявки, списания и последние операции по участнику."
            context["admin_history_timeline"] = self.build_participant_history_timeline(obj)
        return super().render_change_form(
            request,
            context,
            add=add,
            change=change,
            form_url=form_url,
            obj=obj,
        )

    def build_participant_action_links(self, obj: Participant) -> tuple[dict, ...]:
        links = [
            {
                "title": "Найти участника по телефону",
                "url": f"{reverse('admin:users_participant_changelist')}?q={obj.phone}",
            },
            {
                "title": "Открыть заявки участника",
                "url": f"{reverse('admin:referrals_referrallead_changelist')}?q={obj.phone}",
            },
            {
                "title": "Открыть списания участника",
                "url": f"{reverse('admin:bonuses_bonusspendrequest_changelist')}?q={obj.phone}",
            },
            {
                "title": "Открыть бонусные операции",
                "url": f"{reverse('admin:bonuses_bonusledgerentry_changelist')}?q={obj.full_name}",
            },
        ]
        if obj.company:
            links.append(
                {
                    "title": "Найти участников этой компании",
                    "url": f"{reverse('admin:users_participant_changelist')}?q={obj.company}",
                }
            )
            links.append(
                {
                    "title": "Найти заявки этой компании",
                    "url": f"{reverse('admin:referrals_referrallead_changelist')}?q={obj.company}",
                }
            )
        return tuple(links)

    def build_participant_history_timeline(self, obj: Participant) -> tuple[str, ...]:
        history_lines = [f"Текущий баланс: {self.bonus_balance(obj):.2f} мерч-бонусов."]

        referral_link = getattr(obj, "referral_link", None)
        if referral_link:
            invited_leads = (
                ReferralLead.objects.filter(referral_link=referral_link)
                .exclude(client_name=obj.full_name, client_phone=obj.phone)
                .order_by("-created_at")[:3]
            )
            if invited_leads:
                history_lines.append("Последние заявки по ссылке:")
                for lead in invited_leads:
                    history_lines.append(
                        f"{lead.created_at:%d.%m.%Y} — {lead.client_name or 'Клиент без имени'} — "
                        f"{lead.client_company or 'компания не указана'} — {get_lead_status_label(lead.status)}"
                    )

        own_leads = (
            ReferralLead.objects.filter(referral_link__isnull=True, client_phone=obj.phone)
            .order_by("-created_at")[:3]
        )
        if own_leads:
            history_lines.append("Последние свои заявки:")
            for lead in own_leads:
                history_lines.append(
                    f"{lead.created_at:%d.%m.%Y} — {lead.product_interest or 'продукция не указана'} — "
                    f"{get_lead_status_label(lead.status)}"
                )

        bonus_entries = BonusLedgerEntry.objects.filter(participant=obj).order_by("-created_at")[:3]
        if bonus_entries:
            history_lines.append("Последние бонусные операции:")
        for entry in bonus_entries:
            history_lines.append(
                f"{entry.created_at:%d.%m.%Y} — {get_bonus_entry_type_label(entry.entry_type)}: "
                f"{entry.amount:.2f} — {entry.reason}"
            )

        spend_requests = BonusSpendRequest.objects.filter(participant=obj).order_by("-created_at")[:3]
        if spend_requests:
            history_lines.append("Последние списания:")
        for spend_request in spend_requests:
            history_lines.append(
                f"{spend_request.created_at:%d.%m.%Y} — Запрос на списание: "
                f"{spend_request.amount:.2f} — {spend_request.comment or 'без комментария'} "
                f"({get_spend_request_status_label(spend_request.status)})"
            )
        if len(history_lines) == 1:
            history_lines.append("Последних заявок, списаний и бонусных операций пока нет.")
        return tuple(history_lines)

    @admin.display(description="Бонусы")
    def bonus_balance(self, obj: Participant) -> Decimal:
        return calculate_participant_balance(participant=obj)

    @admin.display(description="Баланс")
    def bonus_balance_badge(self, obj: Participant) -> str:
        balance = self.bonus_balance(obj)
        amount = f"{balance:.2f}"
        if balance < 0:
            color = "#9b2226"
            bg = "#fee2e2"
            prefix = ""
        elif balance == 0:
            color = "#5b6470"
            bg = "#e5e7eb"
            prefix = ""
        else:
            color = "#166534"
            bg = "#dcfce7"
            prefix = "+"
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'font-weight:700;color:{};background:{};">{}{}</span>',
            color,
            bg,
            prefix,
            amount,
        )

    @admin.display(description="Компания", ordering="company")
    def company_badge(self, obj: Participant) -> str:
        if not obj.company:
            return format_html(
                '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
                'font-weight:700;color:#92400e;background:#fef3c7;">{}</span>',
                "Без компании",
            )
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'font-weight:700;color:#1d4ed8;background:#dbeafe;">{}</span>',
            obj.company,
        )

    @admin.display(description="Основной контакт", ordering="is_primary_contact")
    def contact_role_badge(self, obj: Participant) -> str:
        if obj.is_primary_contact:
            return format_html(
                '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
                'font-weight:700;color:#166534;background:#dcfce7;">{}</span>',
                "Основной контакт",
            )
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'font-weight:700;color:#5b6470;background:#e5e7eb;">{}</span>',
            "Основной контакт не назначен",
        )

    @admin.display(description="Приглашено")
    @admin.display(description="Участников в компании", ordering="company")
    def company_team_size(self, obj: Participant) -> int:
        if not obj.company:
            return 1
        return Participant.objects.filter(company=obj.company).count()

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

    @admin.display(description="На рассмотрении")
    def pending_spend_requests_count(self, obj: Participant) -> int:
        return BonusSpendRequest.objects.filter(participant=obj, status=SPEND_REQUEST_STATUS_PENDING).count()

    @admin.display(description="Быстрые действия")
    def quick_actions(self, obj: Participant) -> str:
        links = [
            format_html(
                '<a href="{}">Открыть</a>',
                reverse("admin:users_participant_change", args=[obj.pk]),
            ),
            format_html(
                '<a href="{}?client_phone={}">Заявки</a>',
                reverse("admin:referrals_referrallead_changelist"),
                obj.phone,
            ),
            format_html(
                '<a href="{}?q={}">Списания</a>',
                reverse("admin:bonuses_bonusspendrequest_changelist"),
                obj.phone,
            ),
        ]
        if obj.company:
            links.append(
                format_html(
                    '<a href="{}?q={}">Компания</a>',
                    reverse("admin:users_participant_changelist"),
                    obj.company,
                )
            )
        return format_html_join(" ", "{}", ((link,) for link in links))

    @admin.action(description="Выгрузить выбранных участников в CSV")
    def export_selected_to_csv(self, request, queryset):
        rows = []
        for participant in queryset.order_by("-created_at"):
            rows.append(
                [
                    participant.full_name,
                    participant.company,
                    participant.position,
                    participant.phone,
                    participant.telegram_id,
                    "Да" if participant.is_primary_contact else "Нет",
                    f"{self.bonus_balance(participant):.2f}",
                    participant.created_at.strftime("%d.%m.%Y %H:%M"),
                ]
            )
        return build_csv_response(
            filename="participants_export.csv",
            header=[
                "Участник",
                "Компания",
                "Должность",
                "Телефон",
                "Telegram ID",
                "Основной контакт",
                "Баланс",
                "Дата регистрации",
            ],
            rows=rows,
        )


@admin.register(ReferralLead)
class ReferralLeadAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = (
        "lead_type_label",
        "client_company",
        "client_name",
        "client_phone",
        "phone_duplicates_badge",
        "company_duplicates_badge",
        "product_interest",
        "referrer_name",
        "referrer_company",
        "status_badge",
        "quick_actions",
        "created_at",
    )
    search_fields = (
        "client_company",
        "client_name",
        "client_phone",
        "client_email",
        "product_interest",
        "referral_link__participant__full_name",
    )
    list_filter = ("status", "created_at", ReferralLeadSourceFilter, HasAdminCommentFilter, ReferralLeadDuplicateFilter)
    autocomplete_fields = ("referral_link",)
    list_select_related = ("referral_link__participant",)
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = (
        "mark_as_in_progress",
        "mark_as_ordered",
        "mark_as_bonus_confirmed",
        "mark_as_rejected",
        "export_selected_to_csv",
    )
    readonly_fields = ("lead_type_label", "referrer_name", "referrer_company", "created_at")
    fieldsets = (
        ("Клиент", {"fields": ("client_company", "client_name", "client_phone", "client_position", "client_email")}),
        ("Запрос", {"fields": ("product_interest", "quantity", "budget", "deadline")}),
        ("Источник", {"fields": ("lead_type_label", "referral_link", "referrer_name", "referrer_company")}),
        ("Обработка", {"fields": ("status", "rejection_reason", "admin_comment", "created_at")}),
    )
    memo_title = "Проверка реферальной заявки"
    memo_intro = "Перед подтверждением проверьте, что клиент действительно подходит под правила программы."
    memo_items = (
        "Чек-лист перед решением: новый клиент, первая ссылка, нет дублей и самореферала.",
        "Проверьте, новый ли это клиент, и нет ли дубля по телефону, компании или CRM.",
        "Проверьте, не является ли это саморефералом или своей же компанией через другой аккаунт.",
        "Проверьте, что заказ от 2000 BYN, не тендер, не скидка и не спецусловия.",
        "Если одного клиента привели два участника, засчитывается первая ссылка.",
        "Если у компании уже были успешные завершённые заказы, заявка не считается новой рекомендацией.",
        "Комментарий администратора заполнен, если случай спорный или решение требует пояснения.",
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
                    ("Должность", obj.client_position or "Не указана"),
                    ("Email", obj.client_email or "Не указан"),
                    ("Продукция", obj.product_interest or "Не указана"),
                    ("Тираж", obj.quantity or "Не указан"),
                    ("Бюджет", obj.budget or "Не указан"),
                    ("Срок", obj.deadline or "Не указан"),
                    ("Кто пригласил", self.referrer_name(obj)),
                    ("Компания пригласившего", self.referrer_company(obj)),
                    ("Статус заявки", get_lead_status_label(obj.status)),
                    ("Комментарий администратора", obj.admin_comment or "Комментарий пока не добавлен"),
                    ("Причина отказа", obj.rejection_reason or "Пока не указана"),
                    ("Возможные дубли по телефону", self.phone_duplicates_count(obj)),
                    ("Возможные дубли по компании", self.company_duplicates_count(obj)),
                ),
            }
            context["admin_action_links"] = self.build_lead_action_links(obj)
            context["admin_history_title"] = "Операционный контекст заявки"
            context["admin_history_intro"] = "Баланс, последние операции и близкие заявки для быстрой проверки."
            context["admin_history_timeline"] = self.build_lead_operational_context(obj)
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

    @admin.display(description="Статус")
    def status_badge(self, obj: ReferralLead) -> str:
        label = self.status_label(obj)
        color_map = {
            LEAD_STATUS_IN_PROGRESS: ("#1d4ed8", "#dbeafe"),
            LEAD_STATUS_ORDERED: ("#b45309", "#fef3c7"),
            LEAD_STATUS_BONUS_CONFIRMED: ("#166534", "#dcfce7"),
            LEAD_STATUS_REJECTED: ("#b91c1c", "#fee2e2"),
        }
        text_color, bg_color = color_map.get(obj.status, ("#475569", "#e2e8f0"))
        return format_html(
            '<span class="badge" style="display:inline-block;padding:4px 10px;border-radius:999px;font-weight:600;color:{};background:{};">{}</span>',
            text_color,
            bg_color,
            label,
        )

    @admin.display(description="Быстрые действия")
    def quick_actions(self, obj: ReferralLead) -> str:
        links = [
            format_html(
                '<a href="{}">Открыть</a>',
                reverse("admin:referrals_referrallead_change", args=[obj.pk]),
            ),
            format_html(
                '<a href="{}?q={}" style="white-space:nowrap;">Телефон</a>',
                reverse("admin:referrals_referrallead_changelist"),
                obj.client_phone,
            )
        ]
        if obj.client_company:
            links.append(
                format_html(
                    '<a href="{}?q={}" style="white-space:nowrap;">Компания</a>',
                    reverse("admin:referrals_referrallead_changelist"),
                    obj.client_company,
                )
            )
        if obj.client_phone or obj.client_company:
            links.append(
                format_html(
                    '<a href="{}?duplicate_state=yes" style="white-space:nowrap;">Дубли</a>',
                    reverse("admin:referrals_referrallead_changelist"),
                )
            )
        if obj.referral_link:
            links.append(
                format_html(
                    '<a href="{}" style="white-space:nowrap;">Участник</a>',
                    reverse("admin:users_participant_change", args=[obj.referral_link.participant.pk]),
                )
            )
        return format_html_join(" ", "{} ", ((link,) for link in links))

    def phone_duplicates_count(self, obj: ReferralLead) -> int:
        return ReferralLead.objects.filter(client_phone=obj.client_phone).exclude(pk=obj.pk).count()

    def company_duplicates_count(self, obj: ReferralLead) -> int:
        if not obj.client_company:
            return 0
        return ReferralLead.objects.filter(client_company=obj.client_company).exclude(pk=obj.pk).count()

    @admin.display(description="Дубли: телефон")
    def phone_duplicates_badge(self, obj: ReferralLead) -> str:
        count = self.phone_duplicates_count(obj)
        return f"+{count}" if count else "—"

    @admin.display(description="Дубли: компания")
    def company_duplicates_badge(self, obj: ReferralLead) -> str:
        count = self.company_duplicates_count(obj)
        return f"+{count}" if count else "—"

    def build_lead_action_links(self, obj: ReferralLead) -> tuple[dict, ...]:
        links = [
            {
                "title": "Найти заявки по телефону",
                "url": f"{reverse('admin:referrals_referrallead_changelist')}?q={obj.client_phone}",
            }
        ]
        if obj.client_company:
            links.append(
                {
                    "title": "Найти заявки по компании",
                    "url": f"{reverse('admin:referrals_referrallead_changelist')}?q={obj.client_company}",
                }
            )
        if obj.referral_link:
            links.append(
                {
                    "title": "Открыть пригласившего участника",
                    "url": reverse("admin:users_participant_change", args=[obj.referral_link.participant.pk]),
                }
            )
        return tuple(links)

    def build_lead_operational_context(self, obj: ReferralLead) -> tuple[str, ...]:
        context_lines = []
        if obj.referral_link:
            participant = obj.referral_link.participant
            context_lines.append(
                f"Баланс пригласившего: {calculate_participant_balance(participant=participant):.2f} мерч-бонусов."
            )
            bonus_entries = BonusLedgerEntry.objects.filter(participant=participant).order_by("-created_at")[:3]
            if bonus_entries:
                context_lines.append("Последние бонусные операции:")
                context_lines.extend(
                    f"{entry.created_at:%d.%m.%Y} — {get_bonus_entry_type_label(entry.entry_type)}: "
                    f"{entry.amount:.2f} — {entry.reason}"
                    for entry in bonus_entries
                )
            else:
                context_lines.append("Последних бонусных операций нет.")

            spend_requests = BonusSpendRequest.objects.filter(participant=participant).order_by("-created_at")[:3]
            if spend_requests:
                context_lines.append("Последние списания:")
                context_lines.extend(
                    f"{spend_request.created_at:%d.%m.%Y} — "
                    f"{spend_request.comment or 'без комментария'}: {spend_request.amount:.2f} — "
                    f"{get_spend_request_status_label(spend_request.status)}"
                    for spend_request in spend_requests
                )
            else:
                context_lines.append("Последних списаний нет.")
        else:
            context_lines.append("Пригласивший участник не указан.")

        phone_leads = ReferralLead.objects.none()
        if obj.client_phone:
            phone_leads = ReferralLead.objects.filter(client_phone=obj.client_phone).exclude(pk=obj.pk).order_by("-created_at")[:3]
        if phone_leads:
            context_lines.append("Близкие заявки по телефону:")
            context_lines.extend(self.format_related_lead_line(lead) for lead in phone_leads)
        else:
            context_lines.append("Близких заявок по телефону нет.")

        company_leads = ReferralLead.objects.none()
        if obj.client_company:
            company_leads = ReferralLead.objects.filter(client_company=obj.client_company).exclude(pk=obj.pk).order_by("-created_at")[:3]
        if company_leads:
            context_lines.append("Близкие заявки по компании:")
            context_lines.extend(self.format_related_lead_line(lead) for lead in company_leads)
        else:
            context_lines.append("Близких заявок по компании нет.")

        return tuple(context_lines)

    def format_related_lead_line(self, lead: ReferralLead) -> str:
        return (
            f"{lead.created_at:%d.%m.%Y} — {lead.client_name or 'Клиент не указан'} — "
            f"{lead.client_company or 'Компания не указана'} — {get_lead_status_label(lead.status)}"
        )

    @admin.action(description="Перевести в статус «В работе»")
    def mark_as_in_progress(self, request, queryset):
        updated_count = queryset.update(status=LEAD_STATUS_IN_PROGRESS)
        self.message_user(request, f"Заявок переведено в статус «В работе»: {updated_count}.")

    @admin.action(description="Перевести в статус «Ожидает подтверждения»")
    def mark_as_ordered(self, request, queryset):
        updated_count = queryset.update(status=LEAD_STATUS_ORDERED)
        self.message_user(request, f"Заявок переведено в статус «Ожидает подтверждения»: {updated_count}.")

    @admin.action(description="Перевести в статус «Бонус начислен»")
    def mark_as_bonus_confirmed(self, request, queryset):
        updated_count = queryset.update(status=LEAD_STATUS_BONUS_CONFIRMED)
        self.message_user(request, f"Заявок переведено в статус «Бонус начислен»: {updated_count}.")

    @admin.action(description="Перевести в статус «Отклонена»")
    def mark_as_rejected(self, request, queryset):
        updated_count = queryset.update(status=LEAD_STATUS_REJECTED)
        self.message_user(request, f"Заявок переведено в статус «Отклонена»: {updated_count}.")

    @admin.action(description="Выгрузить выбранные заявки в CSV")
    def export_selected_to_csv(self, request, queryset):
        rows = []
        for lead in queryset.order_by("-created_at"):
            rows.append(
                [
                    self.lead_type_label(lead),
                    lead.client_name,
                    lead.client_company,
                    lead.client_phone,
                    lead.client_position,
                    lead.client_email,
                    lead.product_interest,
                    lead.quantity,
                    lead.budget,
                    lead.deadline,
                    self.referrer_name(lead),
                    get_lead_status_label(lead.status),
                    lead.rejection_reason,
                    lead.admin_comment,
                    lead.created_at.strftime("%d.%m.%Y %H:%M"),
                ]
            )
        return build_csv_response(
            filename="referral_leads_export.csv",
            header=[
                "Тип заявки",
                "Клиент",
                "Компания",
                "Телефон",
                "Должность",
                "Email",
                "Продукция",
                "Тираж",
                "Бюджет",
                "Срок",
                "Кто пригласил",
                "Статус",
                "Причина отказа",
                "Комментарий администратора",
                "Дата создания",
            ],
            rows=rows,
        )


@admin.register(ReferralLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "participant")
    search_fields = ("code", "participant__full_name", "participant__phone")
    autocomplete_fields = ("participant",)
    list_select_related = ("participant",)


@admin.register(BonusLedgerEntry)
class BonusLedgerEntryAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = (
        "participant",
        "participant_company",
        "entry_type_label",
        "amount",
        "reason",
        "lead_client",
        "expires_at",
        "quick_actions",
        "created_at",
    )
    search_fields = ("participant__full_name", "reason", "lead__client_name")
    list_filter = ("entry_type", "created_at", BonusLedgerExpirationStateFilter)
    autocomplete_fields = ("participant", "lead")
    list_select_related = ("participant", "lead")
    list_per_page = 25
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "expiration_warning_sent_at")
    fieldsets = (
        ("Операция", {"fields": ("participant", "entry_type", "amount", "reason", "lead", "expires_at", "expiration_warning_sent_at", "created_at")}),
    )
    memo_title = "Проверка бонусной операции"
    memo_intro = "Любая бонусная операция проводится вручную и должна соответствовать правилам программы."
    memo_items = (
        "Основание начисления: заказ оплачен, отгружен и проверен администратором.",
        "Проверьте, что заказ оплачен и отгружен.",
        "Проверьте сумму заказа: бонусы не начисляются по заказам ниже 2000 BYN.",
        "Проверьте, что заказ не тендерный, не низкомаржинальный и без скидки или спецусловий.",
        "Срок сгорания указан для начисления, если бонус должен действовать 12 месяцев.",
        "Если это аннулирование или корректировка, причина аннулирования должна быть понятна из основания.",
        "Если заказ компании делает несколько участников, бонус за заказ компании идёт основному контакту.",
        "При аннулировании после возврата или отмены баланс участника может стать отрицательным — это допустимо.",
    )
    memo_note = "Главный принцип: сначала проверить основание операции, потом подтверждать запись в журнале."

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if obj is not None:
            context["admin_client_card"] = {
                "title": "Карточка бонусной операции",
                "items": (
                    ("Участник", obj.participant.full_name or "Не указан"),
                    ("Компания", obj.participant.company or "Не указана"),
                    ("Тип операции", self.entry_type_label(obj)),
                    ("Сумма", f"{obj.amount:.2f}"),
                    ("Основание", obj.reason or "Не указано"),
                    ("Реферальная заявка", obj.lead.client_name if obj.lead else "Без заявки"),
                    ("Сгорает", obj.expires_at.strftime("%d.%m.%Y") if obj.expires_at else "Не указано"),
                    (
                        "Предупреждение отправлено",
                        obj.expiration_warning_sent_at.strftime("%d.%m.%Y %H:%M")
                        if obj.expiration_warning_sent_at
                        else "Ещё не отправлено",
                    ),
                    ("Дата создания", obj.created_at.strftime("%d.%m.%Y %H:%M")),
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

    @admin.display(description="Тип операции")
    def entry_type_label(self, obj: BonusLedgerEntry) -> str:
        return get_bonus_entry_type_label(obj.entry_type)

    @admin.display(description="Компания")
    def participant_company(self, obj: BonusLedgerEntry) -> str:
        return obj.participant.company or "Не указана"

    @admin.display(description="Клиент")
    def lead_client(self, obj: BonusLedgerEntry) -> str:
        if not obj.lead:
            return "Без заявки"
        return obj.lead.client_name or obj.lead.client_company or "Без имени"

    @admin.display(description="Быстрые действия")
    def quick_actions(self, obj: BonusLedgerEntry) -> str:
        links = [
            format_html(
                '<a href="{}">Участник</a>',
                reverse("admin:users_participant_change", args=[obj.participant_id]),
            )
        ]
        if obj.lead_id:
            links.append(
                format_html(
                    '<a href="{}">Лид</a>',
                    reverse("admin:referrals_referrallead_change", args=[obj.lead_id]),
                )
            )
        if obj.participant.company:
            links.append(
                format_html(
                    '<a href="{}?q={}">Компания</a>',
                    reverse("admin:users_participant_changelist"),
                    obj.participant.company,
                )
            )
        links.append(
            format_html(
                '<a href="{}?q={}">Списания</a>',
                reverse("admin:bonuses_bonusspendrequest_changelist"),
                obj.participant.phone,
            )
        )
        return format_html_join(" ", "{}", ((link,) for link in links))


@admin.register(BonusSpendRequest)
class BonusSpendRequestAdmin(AdminMemoMixin, admin.ModelAdmin):
    list_display = (
        "participant",
        "participant_company",
        "participant_phone",
        "comment",
        "amount",
        "status_badge",
        "quick_actions",
        "created_at",
    )
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
        "Проверьте, что списание не больше 20% суммы заказа.",
        "Проверьте, что списание не больше 200 BYN на один заказ.",
        "Проверьте, что бонусы не используются вместе со скидками или спецусловиями.",
        "Проверьте, что списание не относится к тендерному или низкомаржинальному заказу.",
        "Назначение списания понятно: подарок, доставка, нанесение или часть следующего заказа.",
        "Допустимо использовать бонусы на подарок, доставку, нанесение или часть следующего заказа.",
    )
    memo_note = "Если запрос спорный, оставьте комментарий и принимайте решение вручную."

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if obj is not None:
            context["admin_client_card"] = {
                "title": "Карточка запроса на списание",
                "items": (
                    ("Участник", obj.participant.full_name or "Не указан"),
                    ("Компания", obj.participant.company or "Не указана"),
                    ("Телефон", obj.participant.phone),
                    ("Подарок или комментарий", obj.comment or "Не указано"),
                    ("Сумма", f"{obj.amount:.2f}"),
                    ("Статус", self.status_label(obj)),
                    ("Дата создания", obj.created_at.strftime("%d.%m.%Y %H:%M")),
                ),
            }
            context["admin_action_links"] = (
                {
                    "title": "Открыть участника",
                    "url": reverse("admin:users_participant_change", args=[obj.participant_id]),
                },
                {
                    "title": "Найти заявки этого участника",
                    "url": f'{reverse("admin:referrals_referrallead_changelist")}?client_phone={obj.participant.phone}',
                },
            )
        return super().render_change_form(
            request,
            context,
            add=add,
            change=change,
            form_url=form_url,
            obj=obj,
        )

    @admin.display(description="Телефон")
    def participant_phone(self, obj: BonusSpendRequest) -> str:
        return obj.participant.phone

    @admin.display(description="Компания")
    def participant_company(self, obj: BonusSpendRequest) -> str:
        return obj.participant.company or "Не указана"

    @admin.display(description="Статус")
    def status_label(self, obj: BonusSpendRequest) -> str:
        return get_spend_request_status_label(obj.status)

    @admin.display(description="Статус")
    def status_badge(self, obj: BonusSpendRequest) -> str:
        label = self.status_label(obj)
        color = {
            SPEND_REQUEST_STATUS_PENDING: "#8a6d3b",
            SPEND_REQUEST_STATUS_APPROVED: "#2d6a4f",
            SPEND_REQUEST_STATUS_REJECTED: "#9b2226",
        }.get(obj.status, "#5b6470")
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{}1a;color:{};font-weight:600;">{}</span>',
            color,
            color,
            label,
        )

    @admin.display(description="Быстрые действия")
    def quick_actions(self, obj: BonusSpendRequest) -> str:
        participant_url = reverse("admin:users_participant_change", args=[obj.participant_id])
        leads_url = f"{reverse('admin:referrals_referrallead_changelist')}?client_phone={obj.participant.phone}"
        requests_url = f"{reverse('admin:bonuses_bonusspendrequest_changelist')}?q={obj.participant.phone}"
        company_url = (
            f"{reverse('admin:users_participant_changelist')}?q={obj.participant.company}"
            if obj.participant.company
            else None
        )
        links = [
            format_html('<a href="{}">Участник</a>', participant_url),
            format_html('<a href="{}">Заявки</a>', leads_url),
            format_html('<a href="{}">Списания</a>', requests_url),
        ]
        if company_url:
            links.append(format_html('<a href="{}">Компания</a>', company_url))
        return format_html_join(
            "<br>",
            "{}",
            ((link,) for link in links),
        )

    @admin.action(description="Перевести в статус «Подтверждена»")
    def mark_as_approved(self, request, queryset):
        updated_count = queryset.update(status=SPEND_REQUEST_STATUS_APPROVED)
        self.message_user(request, f"Подтверждено списаний: {updated_count}.")

    @admin.action(description="Перевести в статус «Отклонена»")
    def mark_as_rejected(self, request, queryset):
        updated_count = queryset.update(status=SPEND_REQUEST_STATUS_REJECTED)
        self.message_user(request, f"Отклонено списаний: {updated_count}.")

