GIFT_OFFERS = [
    {
        "slug": "backpack",
        "title": "Рюкзак",
        "amount": 180,
        "description": "Функциональный подарок для сотрудников, партнёров и корпоративных наборов.",
        "is_available": True,
    },
    {
        "slug": "mug",
        "title": "Термокружка",
        "amount": 60,
        "description": "Практичный подарок с логотипом для офиса, встреч и повседневного использования.",
        "is_available": True,
    },
    {
        "slug": "delivery",
        "title": "Доставка",
        "amount": 40,
        "description": "Можно использовать бонусы на доставку по вашему заказу.",
        "is_available": True,
    },
    {
        "slug": "soon_1",
        "title": "Скоро добавим",
        "amount": 0,
        "description": "Здесь появится следующий подарок, когда вы утвердите новые позиции.",
        "is_available": False,
    },
    {
        "slug": "soon_2",
        "title": "Скоро добавим",
        "amount": 0,
        "description": "Оставили место под будущую карточку с изображением и кнопкой выбора.",
        "is_available": False,
    },
]


def get_gift_offer(slug: str) -> dict | None:
    for offer in GIFT_OFFERS:
        if offer["slug"] == slug:
            return offer
    return None
