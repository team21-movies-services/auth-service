import logging
from repositories.base import SQLAlchemyRepository
from models.device import AuthDevice

logger = logging.getLogger(__name__)


class DeviceRepository(SQLAlchemyRepository):
    model = AuthDevice
