from typing import List

import pytest_asyncio
from functional.testdata.roles import fake_role

from models import AuthRole, AuthUser
from repositories.role import RoleRepository


@pytest_asyncio.fixture(scope='session')
async def role_repository(db_session):
    yield RoleRepository(session=db_session)


@pytest_asyncio.fixture()
async def role(fake_role_form, role_repository: RoleRepository):
    return await role_repository.create_role(**fake_role_form)


@pytest_asyncio.fixture()
async def create_fake_roles(db_session):
    async def inner(count) -> List[AuthRole]:
        _roles: List[AuthRole] = [AuthRole(**fake_role()) for _ in range(count)]
        db_session.add_all(_roles)
        await db_session.commit()
        return _roles

    return inner


@pytest_asyncio.fixture()
async def roles(request, create_fake_roles):
    return await create_fake_roles(request.param)


@pytest_asyncio.fixture()
async def roles_with_user(
    request, create_fake_roles, auth_user: AuthUser, role_repository: RoleRepository
) -> List[AuthRole]:
    _roles = await create_fake_roles(request.param)

    await role_repository.add_roles_to_user(auth_user.id, [_role.id for _role in _roles])
    return _roles
