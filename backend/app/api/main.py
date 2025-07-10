from fastapi import APIRouter

from app.api.routes import (
    chatbot,
    feedback,
    formconnect,
    items,
    knowledgebases,
    llms,
    login,
    modelselection,
    private,
    reportgenie,
    sourceretrieval,
    toolfeedback,
    twincheck,
    users,
    utils,
    veradoc,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(knowledgebases.router)
api_router.include_router(formconnect.router)
api_router.include_router(reportgenie.router)
api_router.include_router(veradoc.router)
api_router.include_router(twincheck.router)
api_router.include_router(modelselection.router)
api_router.include_router(llms.router)
api_router.include_router(chatbot.router)
api_router.include_router(sourceretrieval.router)
api_router.include_router(feedback.router, prefix="/api/v1")
api_router.include_router(toolfeedback.router, prefix="/api/v1")


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
