GIFT_OFFERS = [
    {
        "slug": "mug",
        "title": "Термокружка с логотипом",
        "amount": 60,
        "description": "Практичный подарок для сотрудников, партнёров и клиентов.",
    },
    {
        "slug": "notebook",
        "title": "Блокнот + ручка в фирменном стиле",
        "amount": 80,
        "description": "Универсальный набор для welcome pack и деловых встреч.",
    },
    {
        "slug": "hoodie",
        "title": "Худи с брендированием",
        "amount": 150,
        "description": "Подходит для команды, ивентов и корпоративного мерча.",
    },
    {
        "slug": "gift_box",
        "title": "Подарочный набор для клиента",
        "amount": 180,
        "description": "Готовая идея для поздравления, встречи или благодарности.",
    },
    {
        "slug": "delivery",
        "title": "Оплата доставки бонусами",
        "amount": 40,
        "description": "Можно использовать бонусы на доставку по вашему заказу.",
    },
]


def build_gift_button_text(offer: dict) -> str:
    return f"{offer['title']} — {offer['amount']} бонусов"


def get_gift_offer_by_button(button_text: str) -> dict | None:
    for offer in GIFT_OFFERS:
        if build_gift_button_text(offer) == button_text:
            return offer
    return None
