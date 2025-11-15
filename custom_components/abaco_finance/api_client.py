"""Ábaco Finance API Client."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from homeassistant.exceptions import HomeAssistantError


class AbacoFinanceConnectionError(HomeAssistantError):
    """Error to indicate connection failure."""


class AbacoFinanceAuthError(HomeAssistantError):
    """Error to indicate authentication failure."""


class AbacoFinanceClient:
    """Client to interact with Ábaco Finance API."""

    def __init__(
        self,
        api_url: str,
        api_token: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the Ábaco Finance client.
        
        Args:
            api_url: Base URL for the API (e.g., https://api.abacofinance.com.br)
            api_token: API authentication token
            session: aiohttp client session
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.session = session
        self._headers = {
            "X-API-Token": api_token,
            "Content-Type": "application/json",
        }

    async def _request(self, endpoint: str) -> dict[str, Any]:
        """Make a request to the API.
        
        Args:
            endpoint: API endpoint path (e.g., /api/v1/profile)
            
        Returns:
            JSON response as dictionary
            
        Raises:
            AbacoFinanceConnectionError: If connection fails
            AbacoFinanceAuthError: If authentication fails
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            async with asyncio.timeout(10):
                response = await self.session.get(url, headers=self._headers)
                
                if response.status == 401:
                    raise AbacoFinanceAuthError("Invalid API token")
                
                if response.status == 403:
                    raise AbacoFinanceAuthError("Access forbidden")
                
                response.raise_for_status()
                return await response.json()
                
        except asyncio.TimeoutError as err:
            raise AbacoFinanceConnectionError("Timeout connecting to API") from err
        except aiohttp.ClientError as err:
            raise AbacoFinanceConnectionError(f"Error connecting to API: {err}") from err

    async def get_profile(self) -> dict[str, Any]:
        """Get user profile information.
        
        Returns:
            Profile data dictionary
        """
        return await self._request("/api/v1/profile")

    async def get_transactions(self) -> dict[str, Any]:
        """Get transactions data.
        
        Returns:
            Transactions data dictionary
        """
        return await self._request("/api/v1/transactions")

    async def get_accounts(self) -> dict[str, Any]:
        """Get accounts data.
        
        Returns:
            Accounts data dictionary
        """
        return await self._request("/api/v1/accounts")

    async def get_credit_cards(self) -> dict[str, Any]:
        """Get credit cards data.
        
        Returns:
            Credit cards data dictionary
        """
        return await self._request("/api/v1/credit-cards")

    async def get_investments(self) -> dict[str, Any]:
        """Get investments data.
        
        Returns:
            Investments data dictionary
        """
        return await self._request("/api/v1/investments")

    async def get_patrimony(self) -> dict[str, Any]:
        """Obter dados consolidados de patrimônio."""
        return await self._request("/api/v1/assets")

    async def test_connection(self) -> bool:
        """Test the connection to the API.
        
        Returns:
            True if connection is successful
            
        Raises:
            AbacoFinanceConnectionError: If connection fails
            AbacoFinanceAuthError: If authentication fails
        """
        await self.get_profile()
        return True

    async def create_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Cria uma nova transação na API."""
        url = f"{self.api_url}/api/v1/transactions"
        
        try:
            async with asyncio.timeout(10):
                async with self.session.post(url, json=payload, headers=self._headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        return {"success": True, "data": data, "id": data.get("id")}
                    else:
                        error_text = await response.text()
                        return {"success": False, "status": response.status, "error": error_text}
        except asyncio.TimeoutError as err:
            return {"success": False, "error": "Timeout connecting to API"}
        except aiohttp.ClientError as err:
            return {"success": False, "error": f"Connection error: {err}"}