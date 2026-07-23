from aiogram import Router

from apps.bot.handlers import catalog, fallback, gifts, lead, member, spend, start, support


def build_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    router.include_router(member.router)
    router.include_router(catalog.router)
    router.include_router(gifts.router)
    router.include_router(lead.router)
    router.include_router(spend.router)
    router.include_router(support.router)
    router.include_router(fallback.router)
    return router
