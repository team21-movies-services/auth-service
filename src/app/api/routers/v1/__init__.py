from fastapi import APIRouter

from .admin_role import router as admin_role_routers
from .crud_role import router as crud_role_routers
from .info import router as info_routers
from .oauth import router as oauth_router
from .user import router as user_routers

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(user_routers)
v1_router.include_router(info_routers)
v1_router.include_router(crud_role_routers)
v1_router.include_router(admin_role_routers)
v1_router.include_router(oauth_router)
