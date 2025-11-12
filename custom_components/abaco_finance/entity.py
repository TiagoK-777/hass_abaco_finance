"""Ábaco Finance base entity."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity

from . import AbacoFinanceConfigEntry
from .api_client import AbacoFinanceClient, AbacoFinanceConnectionError
from .const import DOMAIN, LOGGER


class AbacoFinanceEntity(Entity):
    """Defines a base Ábaco Finance entity."""

    _attr_has_entity_name = True
    _attr_available = True

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
    ) -> None:
        """Initialize the Ábaco Finance entity."""
        self._entry = entry
        self.client = client

    async def async_update(self) -> None:
        """Update Ábaco Finance entity."""
        if not self.enabled:
            return

        try:
            await self._abaco_update()
            self._attr_available = True
        except AbacoFinanceConnectionError:
            if self._attr_available:
                LOGGER.debug(
                    "An error occurred while updating Ábaco Finance sensor",
                    exc_info=True,
                )
            self._attr_available = False

    async def _abaco_update(self) -> None:
        """Update Ábaco Finance entity."""
        raise NotImplementedError

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Ábaco Finance instance."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="Ábaco Finance",
            name="Ábaco Finance",
            configuration_url=self.client.api_url,
        )
