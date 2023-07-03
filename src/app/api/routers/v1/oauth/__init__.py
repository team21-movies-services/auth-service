from fastapi import APIRouter

from .yandex import router as yandex_router

router = APIRouter(prefix="/oauth")

router.include_router(yandex_router)
