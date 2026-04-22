from fastapi import APIRouter

from . import chat, metrics

api_router = APIRouter(prefix="/api")
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(metrics.router, tags=["metrics"])
