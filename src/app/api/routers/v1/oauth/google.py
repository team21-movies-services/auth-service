import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from schemas.oauth import GoogleOAuthCodeRequestSchema
from schemas.response.user import UserResponse
from services import AuthServiceABC, UserServiceABC
from services.oauth.google import GoogleOAuthServiceABC

router = APIRouter(prefix='/google', tags=['Авторизация через GOOGLE'])
logger = logging.getLogger().getChild('oauth-actions')


@router.get(
    '/login',
    summary="Вход OAuth",
    description="Авторизация пользователя через oauth google: https://developers.google.com/identity/openid-connect/openid-connect",
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
    vk_oauth: GoogleOAuthServiceABC = Depends(),
    user_service: UserServiceABC = Depends(),
    auth_service: AuthServiceABC = Depends(),
) -> UserResponse:
    redirect_uri = request.url_for("_google_callback")
    vk_access_info = await vk_oauth.fetch_access_token(str(redirect_uri), params.code)
    user_info = await vk_oauth.fetch_user_info(vk_access_info)
    user_response = await user_service.get_or_create_user_from_oauth(user_info)
    user_response.tokens = await auth_service.create_token_pair(user_response.id)
    return user_response
