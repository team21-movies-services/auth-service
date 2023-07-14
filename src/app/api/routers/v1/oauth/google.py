import http
import logging

from dependencies.auth import get_auth_data
from domain.oauth.google.response import GoogleOAuthPairTokensResponseSchema
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from schemas.auth import AuthData
from schemas.oauth import GoogleOAuthCodeRequestSchema
from schemas.response.user import UserResponse
from services import AuthServiceABC, UserServiceABC
from services.oauth.google import GoogleOAuthServiceABC

router = APIRouter(prefix='/google', tags=['Авторизация через GOOGLE'])
logger = logging.getLogger().getChild('oauth-actions')


@router.get(
    '/login',
    summary="Вход OAuth",
    description=(
        "Авторизация пользователя через oauth google: "
        "https://developers.google.com/identity/openid-connect/openid-connect"
    ),
    response_class=RedirectResponse,
)
async def _google_login(request: Request, google_oauth: GoogleOAuthServiceABC = Depends()) -> RedirectResponse:
    redirect_uri = request.url_for("_google_callback")
    oauth_authorization_url = google_oauth.create_authorization_url(redirect_uri=str(redirect_uri))
    logger.info(oauth_authorization_url)
    return RedirectResponse(oauth_authorization_url)


@router.get(
    '/callback',
    summary="Коллбэк при успешной авторизации через oauth google",
    response_model=UserResponse,
)
async def _google_callback(
    request: Request,
    params: GoogleOAuthCodeRequestSchema = Depends(),
    google_oauth: GoogleOAuthServiceABC = Depends(),
    user_service: UserServiceABC = Depends(),
    auth_service: AuthServiceABC = Depends(),
) -> UserResponse:
    redirect_uri = request.url_for("_google_callback")
    access_info = await google_oauth.fetch_access_token(str(redirect_uri), params.code)
    user_info = await google_oauth.fetch_user_info(access_info)
    user_response = await user_service.get_or_create_user_from_oauth(user_info)
    user_response.tokens = await auth_service.create_token_pair(user_response.id)
    await google_oauth.add_access_token_to_cache(user_response.id, access_info.access_token, access_info.expires_in)
    await google_oauth.add_refresh_token_to_cache(user_response.id, access_info.refresh_token, access_info.expires_in)
    return user_response


@router.post(
    '/revoke',
    summary="Отозвать токен",
    description=(
        "Отозвать access token google oauth: "
        "https://developers.google.com/identity/protocols/oauth2/web-server#tokenrevoke"
    ),
    status_code=http.HTTPStatus.OK,
)
async def _google_revoke(
    auth_data: AuthData = Depends(get_auth_data),
    google_oauth: GoogleOAuthServiceABC = Depends(),
) -> None:
    await google_oauth.revoke_token(auth_data.user_id)
    await google_oauth.remove_access_token_from_cache(auth_data.user_id)
    await google_oauth.remove_refresh_token_from_cache(auth_data.user_id)


@router.post(
    '/refresh',
    summary="Обновить токен",
    description=(
        "Обновить access token google oauth: "
        "https://developers.google.com/identity/protocols/oauth2/web-server#offline"
    ),
    status_code=http.HTTPStatus.OK,
)
async def _google_refresh(
    auth_data: AuthData = Depends(get_auth_data),
    google_oauth: GoogleOAuthServiceABC = Depends(),
) -> None:
    access_info = await google_oauth.refresh_token(auth_data.user_id)
    await google_oauth.add_access_token_to_cache(auth_data.user_id, access_info.access_token, access_info.expires_in)
    await google_oauth.set_refresh_token_cache_expire(auth_data.user_id, access_info.expires_in)


@router.get(
    '/tokens',
    summary="Получить токены",
    description="Получить google oauth access и refresh токены",
    response_model=GoogleOAuthPairTokensResponseSchema,
)
async def _google_tokens(
    auth_data: AuthData = Depends(get_auth_data),
    google_oauth: GoogleOAuthServiceABC = Depends(),
) -> GoogleOAuthPairTokensResponseSchema:
    return await google_oauth.get_tokens_pair(auth_data.user_id)
