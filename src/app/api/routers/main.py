from api.routers import router as top_router
from fastapi import APIRouter, FastAPI


def setup_routers(app: FastAPI):
    root_router = APIRouter()
    root_router.include_router(top_router)
    app.include_router(root_router)
