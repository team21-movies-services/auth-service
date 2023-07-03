import uuid
from abc import ABC, abstractmethod
from typing import List

from repositories import RoleRepository
from schemas.request.role import RoleRequest
from schemas.response.role import RoleResponse


class RoleServiceABC(ABC):
    @abstractmethod
    async def get_roles_by_user(self, user_id: uuid.UUID) -> List[RoleResponse]:
        ...

    @abstractmethod
    async def get_roles(self) -> List[RoleResponse]:
        ...

    @abstractmethod
    async def add_roles_to_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> None:
        ...

    @abstractmethod
    async def delete_roles_by_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> None:
        ...

    @abstractmethod
    async def create_role(self, role_request: RoleRequest) -> RoleResponse:
        ...

    @abstractmethod
    async def delete_role(self, role_id):
        ...

    @abstractmethod
    async def update_role(self, role_id, role_request: RoleRequest) -> RoleResponse:
        ...


class RoleService(RoleServiceABC):
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def update_role(self, role_id, role_request: RoleRequest) -> RoleResponse:
        role = await self.role_repository.update_by_id(role_id, **role_request.dict())
        return RoleResponse.from_orm(role)

    async def get_roles(self) -> List[RoleResponse]:
        roles = await self.role_repository.get_roles()
        return [RoleResponse.from_orm(role) for role in roles]

    async def get_roles_by_user(self, user_id: uuid.UUID) -> List[RoleResponse]:
        roles = await self.role_repository.get_roles_by_user(user_id)
        return [RoleResponse.from_orm(role) for role in roles]

    async def add_roles_to_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> None:
        await self.role_repository.add_roles_to_user(user_id, role_ids)

    async def delete_roles_by_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> None:
        await self.role_repository.delete_roles_by_user(user_id, role_ids)

    async def create_role(self, role_request: RoleRequest) -> RoleResponse:
        role_db = await self.role_repository.create_role(**role_request.dict(exclude_none=True))
        return RoleResponse.from_orm(role_db)

    async def delete_role(self, role_id) -> None:
        await self.role_repository.delete_by_id(role_id)
