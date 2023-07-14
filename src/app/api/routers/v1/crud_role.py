import logging
import uuid
from typing import List

from common.exceptions.base import ObjectDoesNotExist
from common.exceptions.role import RoleException
from dependencies.auth import get_auth_admin
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.request.role import RoleRequest
from schemas.response.role import RoleResponse
from services.role import RoleServiceABC

router = APIRouter(prefix='/roles', tags=['CRUD для управления ролями'])

logger = logging.getLogger().getChild('crud-role-actions')


@router.get(
    '/',
    summary="Просмотр всех ролей",
    response_model=List[RoleResponse],
    dependencies=[Depends(get_auth_admin)],
)
async def _role_list(
    role_service: RoleServiceABC = Depends(),
) -> List[RoleResponse]:
    logger.debug('View roles')
    return await role_service.get_roles()


@router.post(
    '/',
    summary="Создать роль",
    response_model=RoleResponse,
    dependencies=[Depends(get_auth_admin)],
    status_code=status.HTTP_201_CREATED,
)
async def _create_role(
    role_request: RoleRequest,
    role_service: RoleServiceABC = Depends(),
) -> RoleResponse:
    logger.debug(f'New role: {role_request.dict()}')
    try:
        role_response = await role_service.create_role(role_request)
    except RoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return role_response


@router.delete(
    '/{role_id}',
    summary="Удаление роли",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_auth_admin)],
)
async def _delete_role(
    role_id: uuid.UUID,
    role_service: RoleServiceABC = Depends(),
):
    logger.debug(f'Delete role: role_id - {role_id}')
    try:
        await role_service.delete_role(role_id)
    except RoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.patch(
    '/{role_id}',
    summary="Изменение роли",
    response_model=RoleResponse,
    dependencies=[Depends(get_auth_admin)],
)
async def _update_role(
    role_id: uuid.UUID,
    role_request: RoleRequest,
    role_service: RoleServiceABC = Depends(),
) -> RoleResponse:
    logger.debug(f'Change role: role_id - {role_id}, {role_request.dict()}')
    try:
        role_response = await role_service.update_role(role_id, role_request)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return role_response
