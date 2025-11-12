"""Support for Ábaco Finance."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import AbacoFinanceClient, AbacoFinanceConnectionError
from .const import CONF_API_TOKEN, CONF_API_URL, DOMAIN

PLATFORMS = [Platform.SENSOR]
type AbacoFinanceConfigEntry = ConfigEntry[AbacoFinanceClient]


async def async_setup_entry(
    hass: HomeAssistant, entry: AbacoFinanceConfigEntry
) -> bool:
    """Set up Ábaco Finance from a config entry."""
    session = async_get_clientsession(hass)
    
    client = AbacoFinanceClient(
        api_url=entry.data[CONF_API_URL],
        api_token=entry.data[CONF_API_TOKEN],
        session=session,
    )

    try:
        await client.test_connection()
    except AbacoFinanceConnectionError as exception:
        raise ConfigEntryNotReady from exception

    entry.runtime_data = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AbacoFinanceConfigEntry
) -> bool:
    """Unload Ábaco Finance config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
