import logging
import uuid

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from common.exceptions import AuthException
from dependencies.auth import get_auth_data
from schemas.auth import AuthData
from schemas.oauth import CodeResponse, OAuthTokens, ResponseStatus, OAuthUserInfoSchema
from schemas.response.token import TokensResponse
from services import UserServiceABC, AuthServiceABC
from services.device import DeviceService
from services.oauth.yandex import YandexOAuthServiceABC

router = APIRouter(prefix='/yandex', tags=['Авторизация через сторонние сервисы'])
logger = logging.getLogger().getChild('oauth-actions')


@router.get(
    '/login',
    summary="Вход OAuth",
    description="Авторизация пользователя через oauth yandex",
)
async def _yandex_login(
    request: Request,
    device_service: DeviceService = Depends(),
    yandex_oauth: YandexOAuthServiceABC = Depends(),
) -> RedirectResponse:
    redirect_uri = request.url_for("_yandex_callback")
    device_id = await device_service.get_device_id()

    oauth_authorization_url = yandex_oauth.create_authorization_url(
        redirect_uri=str(redirect_uri),
        device_id=device_id,
    )
    logger.info(oauth_authorization_url)
    return RedirectResponse(oauth_authorization_url)


@router.get(
    '/callback',
    summary="Коллбэк при успешной авторизации через oauth yandex",
)
async def _yandex_callback(
    params: CodeResponse = Depends(),
):
    return {"dsa": 1}

# @router.get(
#     '/tokens',
#     summary="Коллбэк при успешной авторизации в соцсети",
# )
# async def _yandex_tokens(
#     params: CodeResponse = Depends(),
#     user_service: UserServiceABC = Depends(),
#     auth_service: AuthServiceABC = Depends(),
#     yandex_oauth: YandexOAuthService = Depends(),
# ) -> TokensResponse:
#     if not params.code:
#         logger.warning(f'{params.error} - {params.error_description}')
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

#     tokens: OAuthTokens = await yandex_oauth.fetch_token(params.code, params.state)
#     userinfo: OAuthUserInfoSchema = await yandex_oauth.user_info(tokens.access_token)

#     user_id: uuid.UUID = await user_service.get_or_create_user_from_oauth(userinfo)

#     await yandex_oauth.add_access_token_to_cache(user_id, tokens)

#     try:
#         token_response: TokensResponse = await auth_service.create_token_pair(user_id=user_id)
#     except AuthException:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     logger.info(f"Login oauth complete: user_id - {user_id}")
#     return token_response


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
