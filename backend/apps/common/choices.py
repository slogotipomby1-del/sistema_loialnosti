LEAD_STATUS_NEW = "new"
LEAD_STATUS_IN_PROGRESS = "in_progress"
LEAD_STATUS_ORDERED = "ordered"
LEAD_STATUS_BONUS_CONFIRMED = "bonus_confirmed"
LEAD_STATUS_REJECTED = "rejected"

LEAD_STATUS_CHOICES = [
    (LEAD_STATUS_NEW, "Новая"),
    (LEAD_STATUS_IN_PROGRESS, "В работе"),
    (LEAD_STATUS_ORDERED, "Клиент оформил заказ"),
    (LEAD_STATUS_BONUS_CONFIRMED, "Бонус подтверждён"),
    (LEAD_STATUS_REJECTED, "Отказ / не состоялось"),
]
