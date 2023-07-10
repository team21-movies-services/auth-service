import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Header

from common.enums import RateLimitPeriodEnum
from dependencies.common import get_rate_limit
from utils.rate_limit import RateLimiter

from models.history import ActionType
from schemas.request.info import HistoryRequest
from schemas.request.user import UserChangeInfoSchema
from schemas.response.info import HistoryResponse
from schemas.response.role import RoleResponse
from schemas.response.user import UserResponse
from schemas.auth import AuthData
from services import UserServiceABC
from common.exceptions import UserException
from services.history import HistoryServiceABC
from dependencies.auth import get_auth_data
from services.role import RoleServiceABC

router = APIRouter(prefix='/user/info', tags=['Пользовательские данные'])

logger = logging.getLogger().getChild('info-actions')


@router.get(
    '',
    summary="Профиль",
    description="Получение информации о пользователе",
    response_model=UserResponse,
)
async def _user_info(
    user_service: UserServiceABC = Depends(),
    auth_data: AuthData = Depends(get_auth_data),
    rate_limit: RateLimiter = Depends(get_rate_limit),
) -> UserResponse:
    await rate_limit.check_limit(resource='user_info')
    try:
        user_response = await user_service.user_info(auth_data.user_id)
    except UserException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user_response


@router.post(
    '/change',
    summary="Изменение данных",
    description="Изменение информации о личности пользователя",
    response_model=UserResponse,
)
async def _change_user_info(
    request_user_info: UserChangeInfoSchema,
    user_service: UserServiceABC = Depends(),
    history_service: HistoryServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
    auth_data: AuthData = Depends(get_auth_data),
    user_agent: str = Header(),
) -> UserResponse:
    await rate_limit.check_limit(
        resource="user_change", max_requests=5, period=RateLimitPeriodEnum.minutes,
    )

    try:
        user_response = await user_service.change_info(auth_data.user_id, request_user_info)
    except UserException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await history_service.create_history_event(
        user_response.id, user_agent, ActionType.CHANGE_INFO,
    )

    return user_response


@router.get(
    '/history',
    summary="История действий",
    description="История действий пользователя",
    response_model=List[HistoryResponse],
)
async def _history(
    history_request: HistoryRequest = Depends(),
    auth_data: AuthData = Depends(get_auth_data),
    history_service: HistoryServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
) -> List[HistoryResponse]:
    await rate_limit.check_limit(resource='user_login_history')
    history_response_list = await history_service.history_events(
        user_id=auth_data.user_id,
        history_request=history_request,
    )
    return history_response_list


@router.get(
    '/roles',
    summary="Роли",
    description="Роли пользователя",
    response_model=List[RoleResponse],
)
async def _roles(
    auth_data: AuthData = Depends(get_auth_data),
    role_service: RoleServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
) -> List[RoleResponse]:
    await rate_limit.check_limit(resource='user_roles')
    return await role_service.get_roles_by_user(user_id=auth_data.user_id)
