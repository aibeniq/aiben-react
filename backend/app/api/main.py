from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, knowledgebases, formconnect, veradoc, modelselection
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(knowledgebases.router)
api_router.include_router(formconnect.router)
api_router.include_router(veradoc.router)
api_router.include_router(modelselection.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
