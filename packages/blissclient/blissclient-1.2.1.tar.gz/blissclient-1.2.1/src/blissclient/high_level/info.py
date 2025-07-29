from .base import Base
from ..openapi.services.InfoApi_service import _InfoResource_get_get


class Info(Base):
    @property
    def info(self):
        """Get the current bliss rest api info"""
        return _InfoResource_get_get(api_config_override=self._api_config)
