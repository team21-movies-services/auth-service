import logging

from common.enums import SocialNameEnum
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from schemas.oauth import VKOAuthCodeRequestSchema
from schemas.response.user import UserResponse
from services import AuthServiceABC, SocialAccountServiceABC, UserServiceABC
from services.oauth.vk import VKOAuthServiceABC

router = APIRouter(prefix='/vk', tags=['Авторизация через VK'])
logger = logging.getLogger().getChild('oauth-actions')


@router.get(
    '/login',
    summary="Вход OAuth",
    description="Авторизация пользователя через oauth vk: https://vk.com/dev/access_token",
    response_class=RedirectResponse,
)
async def _vk_login(request: Request, vk_oauth: VKOAuthServiceABC = Depends()) -> RedirectResponse:
    redirect_uri = request.url_for("_vk_callback")
    oauth_authorization_url = vk_oauth.create_authorization_url(redirect_uri=str(redirect_uri))
    logger.info(oauth_authorization_url)
    return RedirectResponse(oauth_authorization_url)


@router.get(
    '/callback',
    summary="Коллбэк при успешной авторизации через oauth vk: https://vk.com/dev/access_token",
    response_model=UserResponse,
)
async def _vk_callback(
    request: Request,
    params: VKOAuthCodeRequestSchema = Depends(),
    vk_oauth: VKOAuthServiceABC = Depends(),
    user_service: UserServiceABC = Depends(),
    auth_service: AuthServiceABC = Depends(),
    social_account: SocialAccountServiceABC = Depends(),
) -> UserResponse:
    redirect_uri = request.url_for("_vk_callback")
    vk_access_info = await vk_oauth.fetch_access_token(str(redirect_uri), params.code)
    user_info = await vk_oauth.fetch_user_info(vk_access_info)
    user_response = await social_account.get_user_by_social_account(SocialNameEnum.VK.value, user_info.social_id)
    if not user_response:
        user_response = await user_service.get_or_create_user_from_oauth(user_info)
        await social_account.create_social(SocialNameEnum.VK.value, user_info.social_id, user_response.id)
    user_response.tokens = await auth_service.create_token_pair(user_response.id)
    # TODO: добавить добавление токена в cache
    # await vk_oauth.add_access_token_to_cache(user_response.id, vk_access_info.access_token, vk_access_info.expires_in)
    return user_response
