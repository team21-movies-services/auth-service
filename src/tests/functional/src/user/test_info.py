import json
from http import HTTPStatus
from typing import List

import pytest
from functional.testdata.users import fake_user_info
from httpx import AsyncClient

from models import AuthRole
from models.history import AuthHistory

pytestmark = pytest.mark.asyncio


class TestUserInfo:
    async def test_get_user_info(self, api_client: AsyncClient, auth_tokens, fake_user: dict):
        response = await api_client.get('/api/v1/user/info', headers={'Authorization': auth_tokens['access_token']})
        assert response.status_code == HTTPStatus.OK
        del fake_user['password']
        info = json.loads(response.text)
        assert 'id' in info
        for key in fake_user:
            assert key in info
            assert info[key] == fake_user[key]

    async def test_change_user_info(self, api_client: AsyncClient, auth_tokens):
        new_user_info = fake_user_info()
        response = await api_client.post(
            '/api/v1/user/info/change', json=new_user_info, headers={'Authorization': auth_tokens['access_token']}
        )
        assert response.status_code == HTTPStatus.OK
        info = json.loads(response.text)

        for key in new_user_info:
            assert key in info
            assert info[key] == new_user_info[key]

    @pytest.mark.parametrize("roles_with_user", [3], indirect=True)
    async def test_get_roles(self, api_client: AsyncClient, auth_tokens, roles_with_user: List[AuthRole]):
        response = await api_client.get(
            '/api/v1/user/info/roles', headers={'Authorization': auth_tokens['access_token']}
        )
        assert response.status_code == HTTPStatus.OK
        roles = json.loads(response.text)
        assert len(roles_with_user) == len(roles)
        for i in range(len(roles)):
            assert roles[i]['id'] == str(roles_with_user[i].id)

    @pytest.mark.parametrize("user_history", [4], indirect=True)
    async def test_get_history(self, api_client: AsyncClient, user_history: List[AuthHistory], auth_tokens):
        response = await api_client.get(
            '/api/v1/user/info/history', headers={'Authorization': auth_tokens['access_token']}
        )

        assert response.status_code == HTTPStatus.OK
        history = response.json()
        assert len(history) == len(user_history)

        assert history == sorted(history, key=lambda item: item['created_at'], reverse=True)
