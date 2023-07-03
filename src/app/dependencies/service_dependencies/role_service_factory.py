from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.registrator import add_factory_to_mapper
from dependencies.common import get_session
from services.role import RoleServiceABC, RoleService

from repositories import RoleRepository


@add_factory_to_mapper(RoleServiceABC)
def create_role_service(
        session: AsyncSession = Depends(get_session),
):
    return RoleService(
        RoleRepository(session=session),
    )
