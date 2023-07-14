import json
from typing import List

from httpx import AsyncClient
from http import HTTPStatus
import pytest

from functional.testdata.roles import fake_role
from models import AuthRole

pytestmark = pytest.mark.asyncio


class TestCRUDRoles:
    @pytest.mark.parametrize("roles", [3], indirect=True)
    async def test_view_roles(self, api_client: AsyncClient, admin_auth_token: dict, roles: List[AuthRole]):
        response = await api_client.get('/api/v1/roles/', headers={'Authorization': admin_auth_token['access_token']})
        assert response.status_code == HTTPStatus.OK
        assert len(json.loads(response.text)) == len(roles)

    async def test_create_role(self, api_client: AsyncClient, admin_auth_token: dict, fake_role_form: dict):
        response = await api_client.post(
            '/api/v1/roles/', json=fake_role_form, headers={'Authorization': admin_auth_token['access_token']}
        )
        assert response.status_code == HTTPStatus.CREATED
        role_obj = json.loads(response.text)
        assert role_obj['name'] == fake_role_form['name']
        assert role_obj['description'] == fake_role_form['description']

    async def test_delete_role(self, api_client: AsyncClient, admin_auth_token: dict, role: AuthRole, refresh_object):
        response = await api_client.delete(
            f'/api/v1/roles/{role.id}', headers={'Authorization': admin_auth_token['access_token']}
        )
        assert response.status_code == HTTPStatus.OK
        role = await refresh_object(role)
        assert role is None

    async def test_update_role(self, api_client: AsyncClient, admin_auth_token: dict, role: AuthRole, refresh_object):
        new_fake_role = fake_role()

        response = await api_client.patch(
            f'/api/v1/roles/{role.id}', json=new_fake_role, headers={'Authorization': admin_auth_token['access_token']}
        )
        assert response.status_code == HTTPStatus.OK
        role = await refresh_object(role)
        assert role.name == new_fake_role['name']
        assert role.description == new_fake_role['description']
