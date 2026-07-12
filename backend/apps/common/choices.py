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


def get_lead_status_label(status: str) -> str:
    return LEAD_STATUS_LABELS.get(status, status)


def get_spend_request_status_label(status: str) -> str:
    return SPEND_REQUEST_STATUS_LABELS.get(status, status)
