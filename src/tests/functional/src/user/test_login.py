import pytest
from httpx import AsyncClient
from http import HTTPStatus
from passlib.context import CryptContext
from models import AuthUser

pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=["bcrypt"])


class TestUserAuthActions:
    async def test_login_user(
        self,
        api_client: AsyncClient,
        auth_user: AuthUser,
        fake_user_form_login: dict,
        flushall_redis_data,
    ):
        response = await api_client.post('/api/v1/user/login', json=fake_user_form_login)
        tokens = response.json()
        assert response.status_code == HTTPStatus.OK
        assert tokens['access_token']
        assert tokens['refresh_token']

    async def test_error_login_user(
        self,
        api_client: AsyncClient,
        fake_user_form_login: dict,
    ):
        response = await api_client.post('/api/v1/user/login', json=fake_user_form_login)
        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_change_password(
        self, api_client: AsyncClient, auth_tokens, password_change_form, auth_user: AuthUser, refresh_object
    ):
        headers = {'Authorization': auth_tokens['access_token']}
        response = await api_client.post('/api/v1/user/password/change', json=password_change_form, headers=headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        user: AuthUser = await refresh_object(auth_user)
        assert pwd_context.verify(password_change_form['new_password'], user.password)

    async def test_refresh_tokens(self, api_client: AsyncClient, auth_tokens):
        data = {'refresh_token': auth_tokens['refresh_token']}
        response = await api_client.post('/api/v1/user/refresh/token', json=data)
        tokens = response.json()
        assert response.status_code == HTTPStatus.OK
        assert tokens['access_token']
        assert tokens['refresh_token']
