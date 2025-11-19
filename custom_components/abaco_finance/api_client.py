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
            async with asyncio.timeout(60):
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

    async def get_transactions(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        status: str | None = None,
        transaction_type: str | None = None,
        limit: int = 50,
        auto_paginate: bool = True,
    ) -> dict[str, Any]:
        """Get transactions data with optional filters and automatic pagination.
        
        Args:
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            status: Filter by status: 'pending' or 'paid' (optional)
            transaction_type: Filter by type: 'income' or 'expense' (optional)
            limit: Maximum items per page (default: 50)
            auto_paginate: Automatically fetch all pages (default: True)
        
        Returns:
            Transactions data dictionary with structure:
            {
                "data": [...],  # List of transactions
                "total_count": int,  # Total items across all pages
                "has_more": bool,  # Whether more pages exist
                "pages_fetched": int  # Number of pages fetched
            }
        """
        from .const import LOGGER
        
        endpoint = "/api/v1/transactions"
        params = []
        
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        if status:
            params.append(f"status={status}")
        if transaction_type:
            params.append(f"type={transaction_type}")
        
        params.append(f"limit={limit}")
        
        # Build initial URL
        query_string = "&".join(params)
        full_endpoint = f"{endpoint}?{query_string}"
        
        LOGGER.debug("Buscando transações: %s (auto_paginate=%s)", full_endpoint, auto_paginate)
        
        # Fetch first page
        first_page = await self._request(full_endpoint)
        
        if not auto_paginate or not isinstance(first_page, dict):
            # Return single page result
            return first_page
        
        # Initialize aggregated result
        all_transactions = first_page.get("data", [])
        total_count = first_page.get("total", len(all_transactions))
        pages_fetched = 1
        
        # Check if there are more pages
        has_more = first_page.get("has_more", False)
        next_cursor = first_page.get("next_cursor")
        
        # Fetch remaining pages if auto_paginate is enabled
        while has_more and next_cursor:
            params_with_cursor = params + [f"cursor={next_cursor}"]
            paginated_endpoint = f"{endpoint}?{'&'.join(params_with_cursor)}"
            
            LOGGER.debug("Buscando página adicional: cursor=%s", next_cursor)
            
            try:
                page_data = await self._request(paginated_endpoint)
                
                if isinstance(page_data, dict):
                    page_transactions = page_data.get("data", [])
                    all_transactions.extend(page_transactions)
                    pages_fetched += 1
                    
                    has_more = page_data.get("has_more", False)
                    next_cursor = page_data.get("next_cursor")
                    
                    LOGGER.debug(
                        "Página %d buscada: %d transações (total acumulado: %d)",
                        pages_fetched,
                        len(page_transactions),
                        len(all_transactions)
                    )
                else:
                    LOGGER.warning("Resposta de paginação inválida, interrompendo")
                    break
                    
            except Exception as e:
                LOGGER.error("Erro ao buscar página adicional: %s", e)
                break
        
        # Return aggregated result
        result = {
            "data": all_transactions,
            "total_count": total_count,
            "has_more": False,  # All pages fetched
            "pages_fetched": pages_fetched,
        }
        
        LOGGER.info(
            "Transações obtidas: %d itens em %d página(s) (total_count=%d)",
            len(all_transactions),
            pages_fetched,
            total_count
        )
        
        return result

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