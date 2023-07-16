import json
from http import HTTPStatus
from typing import List

import pytest
from httpx import AsyncClient

from models import AuthRole, AuthUser
from repositories import RoleRepository

pytestmark = pytest.mark.asyncio


class TestAdminRoles:
    @pytest.mark.parametrize("roles_with_user", [3], indirect=True)
    async def test_view_roles_user(
        self, api_client: AsyncClient, admin_auth_token: dict, auth_user: AuthUser, roles_with_user: List[AuthRole]
    ):
        response = await api_client.get(
            f'/api/v1/users/{auth_user.id}/roles', headers={'Authorization': admin_auth_token['access_token']}
        )
        roles = json.loads(response.text)
        assert response.status_code == HTTPStatus.OK
        assert len(roles) == len(roles_with_user)
        for i in range(len(roles)):
            assert roles[i]['id'] == str(roles_with_user[i].id)
            assert roles[i]['name'] == roles_with_user[i].name
            assert roles[i]['description'] == roles_with_user[i].description

    @pytest.mark.parametrize("roles", [3], indirect=True)
    async def test_add_roles_to_user(
        self,
        api_client: AsyncClient,
        admin_auth_token: dict,
        auth_user: AuthUser,
        roles: List[AuthRole],
        role_repository: RoleRepository,
    ):
        role_ids = [str(role.id) for role in roles]
        response = await api_client.post(
            f'/api/v1/users/{auth_user.id}/roles',
            json=role_ids,
            headers={'Authorization': admin_auth_token['access_token']},
        )
        assert response.status_code == HTTPStatus.OK
        roles_db = await role_repository.get_roles_by_user(auth_user.id)

        assert len(roles) == len(roles_db)
        for i in range(len(roles)):
            assert roles_db[i].id == roles[i].id
            assert roles_db[i].name == roles[i].name
            assert roles_db[i].description == roles[i].description

    @pytest.mark.parametrize("roles_with_user", [3], indirect=True)
    async def test_delete_roles_to_user(
        self,
        api_client: AsyncClient,
        admin_auth_token: dict,
        auth_user: AuthUser,
        roles_with_user: List[AuthRole],
        role_repository: RoleRepository,
    ):
        role_ids = [str(role.id) for role in roles_with_user]
        response = await api_client.request(
            'DELETE',
            url=f'/api/v1/users/{auth_user.id}/roles',
            json=role_ids,
            headers={'Authorization': admin_auth_token['access_token']},
        )
        assert response.status_code == HTTPStatus.OK
        roles_db = await role_repository.get_roles_by_user(auth_user.id)
        assert not roles_db
