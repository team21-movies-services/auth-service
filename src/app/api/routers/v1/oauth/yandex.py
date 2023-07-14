import logging

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from common.exceptions import AuthException
from dependencies.auth import get_auth_data
from schemas.auth import AuthData
from schemas.oauth import (
    OAuthCodeRequestSchema,
    OAuthTokens,
    ResponseStatus,
    OAuthUserInfoSchema,
)
from schemas.response.user import UserResponse
from schemas.response.token import TokensResponse
from services import UserServiceABC, AuthServiceABC
from services.device import DeviceService
from services.oauth.yandex import YandexOAuthServiceABC

from domain.oauth.dto import OAuthTokenDto, OAuthUserInfoDto
from domain.oauth.yandex.dto import AuthorizationUrlDto, OAuthRequestTokenDto


router = APIRouter(prefix="/yandex", tags=["Авторизация через сторонние сервисы"])
logger = logging.getLogger().getChild("oauth-actions")


@router.get(
    "/login",
    summary="Вход OAuth",
    description="Авторизация пользователя через oauth yandex",
)
async def _yandex_login(
    request: Request,
    device_service: DeviceService = Depends(),
    yandex_oauth_service: YandexOAuthServiceABC = Depends(),
) -> RedirectResponse:
    redirect_uri = request.url_for("_yandex_callback")
    device_id = await device_service.get_device_id()
    auth_url_dto = AuthorizationUrlDto(
        redirect_uri=str(redirect_uri),
        device_id=device_id,
    )
    oauth_authorization_url = yandex_oauth_service.create_authorization_url(auth_url_dto)
    logger.info(oauth_authorization_url)
    return RedirectResponse(oauth_authorization_url)


@router.get(
    "/callback",
    summary="Коллбэк при успешной авторизации через oauth yandex",
)
async def _yandex_callback(
    oauth_code_req: OAuthCodeRequestSchema = Depends(),
    yandex_oauth_service: YandexOAuthServiceABC = Depends(),
    user_service: UserServiceABC = Depends(),
    auth_service: AuthServiceABC = Depends(),
) -> UserResponse:
    if not oauth_code_req.code:
        logger.warning(f"{oauth_code_req.error} - {oauth_code_req.error_description}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    oauth_request_token = OAuthRequestTokenDto(
        code=oauth_code_req.code, state=oauth_code_req.state,
    )
    token_dto = await yandex_oauth_service.fetch_token(
        oauth_request_token,
    )
    user_info = await yandex_oauth_service.user_info(token_dto)
    user_response = await user_service.get_or_create_user_from_oauth(user_info)
    user_response.tokens = await auth_service.create_token_pair(user_response.id)
    return user_response

# #
# # @router.post('/refresh')
# # async def _yandex_refresh(refresh_token: str,
# #                           yandex_oauth: YandexOAuthService = Depends()) -> OAuthTokens:
# #     return await yandex_oauth.refresh_tokens(refresh_token)


# @router.post(
#     '/revoke',
#     summary="Отвязать соцсеть",
#     description="Открепить аккаунт в соцсети от личного кабинета",
# )
# async def _yandex_revoke(
#     auth_data: AuthData = Depends(get_auth_data),
#     yandex_oauth: YandexOAuthService = Depends(),
# ) -> ResponseStatus:
#     return await yandex_oauth.revoke_token(auth_data.user_id)
