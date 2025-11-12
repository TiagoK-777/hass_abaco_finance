"""Config flow to configure the Ábaco Finance integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import (
    AbacoFinanceAuthError,
    AbacoFinanceClient,
    AbacoFinanceConnectionError,
)
from .const import CONF_API_TOKEN, CONF_API_URL, DEFAULT_API_URL, DOMAIN


class AbacoFinanceFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle an Ábaco Finance config flow."""

    VERSION = 1

    async def _show_setup_form(
        self, errors: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
                    vol.Required(CONF_API_TOKEN): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if user_input is None:
            return await self._show_setup_form()

        errors = {}

        # Normalize API URL
        api_url = user_input[CONF_API_URL].rstrip("/")
        
        # Check if already configured
        await self.async_set_unique_id(user_input[CONF_API_TOKEN][:16])
        self._abort_if_unique_id_configured()

        session = async_get_clientsession(self.hass)

        client = AbacoFinanceClient(
            api_url=api_url,
            api_token=user_input[CONF_API_TOKEN],
            session=session,
        )

        try:
            await client.test_connection()
        except AbacoFinanceAuthError:
            errors["base"] = "invalid_auth"
            return await self._show_setup_form(errors)
        except AbacoFinanceConnectionError:
            errors["base"] = "cannot_connect"
            return await self._show_setup_form(errors)

        return self.async_create_entry(
            title="Ábaco Finance",
            data={
                CONF_API_URL: api_url,
                CONF_API_TOKEN: user_input[CONF_API_TOKEN],
            },
        )
