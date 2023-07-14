from http import HTTPStatus

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestRegistration:
    async def test_create_user(self, api_client: AsyncClient, fake_user_form_registration):
        response = await api_client.post('/api/v1/user/registration', json=fake_user_form_registration)
        assert response.status_code == HTTPStatus.CREATED

    async def test_create_already_exist_user(self, api_client: AsyncClient, auth_user, fake_user_form_registration):
        response = await api_client.post('/api/v1/user/registration', json=fake_user_form_registration)
        assert response.status_code == HTTPStatus.CONFLICT
