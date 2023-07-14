import logging

from common.enums import RateLimitPeriodEnum
from common.exceptions import AuthException, UserAlreadyExists, UserException
from dependencies.auth import get_auth_data, get_refresh_data
from dependencies.common import get_rate_limit
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import Response
from models.history import ActionType
from schemas.auth import AuthData, RefreshData
from schemas.request.user import (
    UserChangePasswordSchema,
    UserLoginSchema,
    UserRegistrationSchema,
)
from schemas.response.token import TokensResponse
from schemas.response.user import UserResponse
from services import AuthServiceABC, HistoryServiceABC, UserServiceABC
from utils.rate_limit import RateLimiter

router = APIRouter(prefix="/user", tags=["Регистрационные действия"])

logger = logging.getLogger().getChild("auth-actions")


@router.post(
    "/registration",
    summary="Регистрация",
    description="Регистрация пользователей в системе",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def _registration(
    request_user: UserRegistrationSchema,
    user_service: UserServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
) -> UserResponse:
    await rate_limit.check_limit(resource="user_registration")

    logger.debug(f"Registration: {request_user.safe_data()}")
    try:
        user_response = await user_service.create_user(request_user)
    except UserAlreadyExists:
        logger.debug(f"Registration conflict: {request_user.safe_data()}")
        raise HTTPException(status.HTTP_409_CONFLICT)

    logger.info(f'Registering a new user: {user_response.json(include={"email"})}')
    return user_response


@router.post(
    "/login",
    summary="Логин",
    description="Вход пользователя в аккаунт",
)
async def _login(
    request_login: UserLoginSchema,
    user_service: UserServiceABC = Depends(),
    auth_service: AuthServiceABC = Depends(),
    history_service: HistoryServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
    user_agent: str = Header(),
) -> UserResponse:
    await rate_limit.check_limit(resource="user_login", max_requests=5)

    logger.info(f"Login: {request_login.json(exclude={'password'})}")
    try:
        user_response = await user_service.login(request_login)
    except UserException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        tokens: TokensResponse = await auth_service.create_token_pair(
            user_id=user_response.id,
            is_superuser=user_response.is_superuser,
        )
    except AuthException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user_response.tokens = tokens

    await history_service.create_history_event(
        user_response.id,
        user_agent,
        ActionType.LOGIN,
    )
    logger.info(f"Login complete: {user_response.json(include={'email'})}")
    return user_response


@router.post(
    "/refresh/token",
    summary="Обновление токена",
)
async def _refresh_token(
    auth_service: AuthServiceABC = Depends(),
    refresh_data: RefreshData = Depends(get_refresh_data),
):
    await auth_service.remove_refresh_token_from_cache(refresh_data.refresh_token)

    try:
        token_response: TokensResponse = await auth_service.create_token_pair(
            user_id=refresh_data.user_id,
            is_superuser=refresh_data.is_superuser,
        )
    except AuthException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return token_response


@router.post(
    "/password/change",
    summary="Изменение пароля",
    description="Изменение пароля пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def _password_change(
    request_change_password: UserChangePasswordSchema,
    user_service: UserServiceABC = Depends(),
    rate_limit: RateLimiter = Depends(get_rate_limit),
    history_service: HistoryServiceABC = Depends(),
    auth_data: AuthData = Depends(get_auth_data),
    user_agent: str = Header(),
):
    logger.info(f"Change password: user_id - {auth_data.user_id}")
    await rate_limit.check_limit(
        resource="user_registration",
        max_requests=5,
        period=RateLimitPeriodEnum.minutes,
    )

    try:
        user_response = await user_service.password_change(
            auth_data.user_id,
            request_change_password,
        )
    except UserException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await history_service.create_history_event(
        user_response.id,
        user_agent,
        ActionType.CHANGE_PASSWORD,
    )
    logger.info(f"Change password complete: user_id - {auth_data.user_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/logout",
    summary="Выход из аккаунта",
    description="Выход из аккаунта пользователя",
    status_code=status.HTTP_200_OK,
)
async def _logout(
    auth_service: AuthServiceABC = Depends(),
    refresh_data: RefreshData = Depends(get_refresh_data),
):
    logger.info(f"Logout: user_id - {refresh_data.user_id}")
    await auth_service.remove_refresh_token_from_cache(refresh_data.refresh_token)
