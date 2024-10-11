from fastapi import APIRouter
from .routes import chat

router = APIRouter()

router.include_router(chat.router, prefix="/api/v1", tags=["chat"])
