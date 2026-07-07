from aiogram import Router

from apps.bot.handlers import lead, member, spend, start


def build_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    router.include_router(member.router)
    router.include_router(lead.router)
    router.include_router(spend.router)
    return router
