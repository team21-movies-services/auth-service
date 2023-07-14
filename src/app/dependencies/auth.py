import logging
from typing import Optional
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader

from services import AuthServiceABC
from schemas.auth import AuthData, RefreshData
from common.exceptions.auth import TokenException, TokenExpiredException

from schemas.request.token import RefreshSchema

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

logger = logging.getLogger().getChild('auth')


async def get_refresh_data(
    request_refresh_data: RefreshSchema,
    auth_service: AuthServiceABC = Depends(),
) -> RefreshData:
    try:
        refresh_data: RefreshData = await auth_service.validate_refresh_token(request_refresh_data.refresh_token)
    except TokenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"message": "Error validating refresh token: Session has expired"}},
        )
    logger.debug(f'User refresh token: user_id - {refresh_data.user_id}')
    return refresh_data


async def get_auth_data(
    auth_service: AuthServiceABC = Depends(),
    access_token: Optional[str] = Security(api_key_header),
):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        auth_data: AuthData = await auth_service.validate_access_token(access_token)
    except TokenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"message": "Error validating access token: Session has expired"}},
        )
    logger.debug(f'User request: user_id - {auth_data.user_id}')
    return auth_data


async def get_auth_admin(
    auth_data: AuthData = Depends(get_auth_data),
):
    if not auth_data.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return auth_data
