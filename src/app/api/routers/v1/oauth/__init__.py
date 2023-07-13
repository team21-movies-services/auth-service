from fastapi import APIRouter

from .yandex import router as yandex_router
from .vk import router as vk_router
from .google import router as google_router

router = APIRouter(prefix="/oauth")

router.include_router(yandex_router)
router.include_router(vk_router)
router.include_router(google_router)
