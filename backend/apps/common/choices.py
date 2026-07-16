LEAD_STATUS_NEW = "new"
LEAD_STATUS_IN_PROGRESS = "in_progress"
LEAD_STATUS_ORDERED = "ordered"
LEAD_STATUS_BONUS_CONFIRMED = "bonus_confirmed"
LEAD_STATUS_REJECTED = "rejected"

LEAD_STATUS_LABELS = {
    LEAD_STATUS_NEW: "Новая",
    LEAD_STATUS_IN_PROGRESS: "В работе",
    LEAD_STATUS_ORDERED: "Ожидает подтверждения",
    LEAD_STATUS_BONUS_CONFIRMED: "Бонус начислен",
    LEAD_STATUS_REJECTED: "Отклонена",
}

LEAD_STATUS_CHOICES = list(LEAD_STATUS_LABELS.items())

SPEND_REQUEST_STATUS_PENDING = "pending"
SPEND_REQUEST_STATUS_APPROVED = "approved"
SPEND_REQUEST_STATUS_REJECTED = "rejected"

SPEND_REQUEST_STATUS_LABELS = {
    SPEND_REQUEST_STATUS_PENDING: "На рассмотрении",
    SPEND_REQUEST_STATUS_APPROVED: "Подтверждена",
    SPEND_REQUEST_STATUS_REJECTED: "Отклонена",
}

SPEND_REQUEST_STATUS_CHOICES = list(SPEND_REQUEST_STATUS_LABELS.items())

BONUS_ENTRY_TYPE_ACCRUAL = "accrual"
BONUS_ENTRY_TYPE_REVERSAL = "reversal"
BONUS_ENTRY_TYPE_EXPIRATION = "expiration"
BONUS_ENTRY_TYPE_MANUAL_ADJUSTMENT = "manual_adjustment"

BONUS_ENTRY_TYPE_LABELS = {
    BONUS_ENTRY_TYPE_ACCRUAL: "Начисление",
    BONUS_ENTRY_TYPE_REVERSAL: "Аннулирование",
    BONUS_ENTRY_TYPE_EXPIRATION: "Сгорание",
    BONUS_ENTRY_TYPE_MANUAL_ADJUSTMENT: "Ручная корректировка",
}

BONUS_ENTRY_TYPE_CHOICES = list(BONUS_ENTRY_TYPE_LABELS.items())


def get_lead_status_label(status: str) -> str:
    return LEAD_STATUS_LABELS.get(status, status)


def get_spend_request_status_label(status: str) -> str:
    return SPEND_REQUEST_STATUS_LABELS.get(status, status)


def get_bonus_entry_type_label(entry_type: str) -> str:
    return BONUS_ENTRY_TYPE_LABELS.get(entry_type, entry_type)
