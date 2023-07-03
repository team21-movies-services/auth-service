from fastapi import APIRouter, status

router = APIRouter(tags=['Служебные'])


@router.get("/healthcheck", status_code=status.HTTP_200_OK)
def healthcheck():
    return {"success": 1}
