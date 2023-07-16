from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.common import get_session
from dependencies.registrator import add_factory_to_mapper
from repositories import RoleRepository
from services.role import RoleService, RoleServiceABC


@add_factory_to_mapper(RoleServiceABC)
def create_role_service(
    session: AsyncSession = Depends(get_session),
):
    return RoleService(
        RoleRepository(session=session),
    )
