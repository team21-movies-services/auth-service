from fastapi import APIRouter

from .yandex import router as yandex_router
from .vk import router as vk_router

router = APIRouter(prefix="/oauth")

router.include_router(yandex_router)
router.include_router(vk_router)
