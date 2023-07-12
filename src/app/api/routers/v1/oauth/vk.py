import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from services.oauth.vk import VKOAuthServiceABC
from schemas.oauth import CodeResponse
from domain.oauth.vk.response import OAuthResponseTokenSchema

router = APIRouter(prefix='/vk', tags=['Авторизация через VK'])
logger = logging.getLogger().getChild('oauth-actions')


@router.get(
    '/login',
    summary="Вход OAuth",
    description="Авторизация пользователя через oauth vk",
    response_class=RedirectResponse,
)
async def _vk_login(request: Request, vk_oauth: VKOAuthServiceABC = Depends()):
    redirect_uri = request.url_for("_vk_callback")
    oauth_authorization_url = vk_oauth.create_authorization_url(redirect_uri=str(redirect_uri))
    logger.info(oauth_authorization_url)
    return RedirectResponse(oauth_authorization_url)


@router.get(
    '/callback',
    summary="Коллбэк при успешной авторизации через oauth vk",
    response_model=OAuthResponseTokenSchema,
)
async def _vk_callback(request: Request, params: CodeResponse = Depends(), vk_oauth: VKOAuthServiceABC = Depends()):
    if not params.code:
        # TODO: raise error
        return
    redirect_uri = request.url_for("_vk_callback")
    oauth_access_url = vk_oauth.fetch_access_token(str(redirect_uri), params.code)
    return oauth_access_url
