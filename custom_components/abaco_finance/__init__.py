"""Support for Ábaco Finance."""

from __future__ import annotations

import voluptuous as vol
from datetime import date
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import AbacoFinanceClient, AbacoFinanceConnectionError
from .const import CONF_API_TOKEN, CONF_API_URL, DOMAIN

PLATFORMS = [Platform.SENSOR]
type AbacoFinanceConfigEntry = ConfigEntry[AbacoFinanceClient]

SERVICE_ABACO_TRANSACTION = "abaco_transaction"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("amount"): cv.positive_float,
    vol.Required("description"): cv.string,
    vol.Required("credit_card_id"): cv.string,
    vol.Required("category_id"): cv.string,
})


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

    # Registrar serviço de transação
    async def handle_abaco_transaction(call: ServiceCall) -> None:
        """Handle abaco transaction service."""
        client: AbacoFinanceClient = entry.runtime_data
        
        payload = {
            "type": "expense",
            "amount": float(call.data["amount"]),
            "transaction_date": date.today().isoformat(),
            "credit_card_id": call.data["credit_card_id"],
            "category_id": call.data["category_id"],
            "description": call.data["description"],
            "status": "paid",
            "is_recurring": False,
            "is_installment": False
        }
        
        result = await client.create_transaction(payload)
        hass.bus.fire("abaco_transaction_result", result)

    hass.services.async_register(
        DOMAIN, SERVICE_ABACO_TRANSACTION, handle_abaco_transaction, schema=SERVICE_SCHEMA
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AbacoFinanceConfigEntry
) -> bool:
    """Unload Ábaco Finance config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
