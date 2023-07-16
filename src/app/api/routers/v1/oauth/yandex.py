import logging

from common.enums import SocialNameEnum
from dependencies.auth import get_auth_data
from domain.oauth.yandex.dto import AuthorizationUrlDto, CacheTokensDto, OAuthRequestTokenDto
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from schemas.auth import AuthData
from schemas.oauth import OAuthCodeRequestSchema
from schemas.response.user import UserResponse
from services import AuthServiceABC, SocialAccountServiceABC, UserServiceABC
from services.device import DeviceService
from services.oauth.yandex import YandexOAuthServiceABC

router = APIRouter(prefix="/yandex", tags=["Авторизация через YANDEX"])

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
    social_account: SocialAccountServiceABC = Depends(),
) -> UserResponse:
    if not oauth_code_req.code:
        logger.warning(f"{oauth_code_req.error} - {oauth_code_req.error_description}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    oauth_request_token = OAuthRequestTokenDto(code=oauth_code_req.code, state=oauth_code_req.state)
    token_dto = await yandex_oauth_service.fetch_token(oauth_request_token)
    user_info = await yandex_oauth_service.user_info(token_dto)
    user_response = await social_account.get_user_by_social_account(SocialNameEnum.YANDEX.value, user_info.social_id)
    if not user_response:
        user_response = await user_service.get_or_create_user_from_oauth(user_info)
        await social_account.create_social(SocialNameEnum.YANDEX.value, user_info.social_id, user_response.id)
    user_response.tokens = await auth_service.create_token_pair(user_response.id)
    cache_tokens_dto = CacheTokensDto(
        user_id=user_response.id,
        access_token=token_dto.access_token,
        refresh_token=token_dto.refresh_token,
        expired=token_dto.expires_in,
    )
    await yandex_oauth_service.add_tokens_to_cache(cache_tokens_dto)
    return user_response


@router.post(
    "/refresh",
    summary="Обновить токен",
    description=("Обновить access token yandex oauth: https://yandex.ru/dev/id/doc/ru/tokens/refresh-client"),
)
async def _yandex_refresh(
    auth_data: AuthData = Depends(get_auth_data),
    yandex_oauth_service: YandexOAuthServiceABC = Depends(),
    status_code=status.HTTP_200_OK,
) -> None:
    access_info = await yandex_oauth_service.refresh_token(auth_data.user_id)
    cache_tokens_dto = CacheTokensDto(
        user_id=auth_data.user_id,
        access_token=access_info.access_token,
        refresh_token=access_info.refresh_token,
        expired=access_info.expires_in,
    )
    await yandex_oauth_service.add_tokens_to_cache(cache_tokens_dto)


@router.post(
    "/revoke",
    summary="Отозвать токен",
    description=("Отозвать access token yandex oauth: https://yandex.ru/dev/id/doc/ru/tokens/token-invalidate"),
    status_code=status.HTTP_200_OK,
)
async def _yandex_revoke(
    auth_data: AuthData = Depends(get_auth_data),
    yandex_oauth_service: YandexOAuthServiceABC = Depends(),
) -> None:
    await yandex_oauth_service.revoke_token(auth_data.user_id)
    await yandex_oauth_service.remove_tokens_from_cache(auth_data.user_id)
