"""Suporte para sensores do Ábaco Finance."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AbacoFinanceConfigEntry
from .api_client import AbacoFinanceClient
from .const import DOMAIN
from .entity import AbacoFinanceEntity

SCAN_INTERVAL = timedelta(minutes=5)
PARALLEL_UPDATES = 4


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AbacoFinanceConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura os sensores do Ábaco Finance com base em uma config entry."""
    client = entry.runtime_data
    entities = []

    # Buscar dados iniciais para criar sensores dinamicamente
    try:
        cards_data = await client.get_credit_cards()
        accounts_data = await client.get_accounts()
        investments_data = await client.get_investments()
        patrimony_data = await client.get_patrimony()
    except Exception:
        cards_data = {"cards": []}
        accounts_data = {"accounts": []}
        investments_data = []
        patrimony_data = {}

    # Sensores do endpoint Profile
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "profile", "name", "Nome", icon="mdi:account"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "profile", "email", "Email", icon="mdi:email"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "profile", "default_currency", "Moeda Padrão", icon="mdi:currency-usd"
    ))

    # Endpoint Accounts: um sensor por conta + sensores de resumo, todos no dispositivo "Contas"

    # One sensor per account
    for account in accounts_data.get("accounts", []):
        entities.append(AbacoFinanceAccountSensor(client, entry, account))

    # Summary sensors (use same "Contas" device)
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "accounts", "total_accounts", "Total de Contas", icon="mdi:counter"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "accounts", "summary.0.total_balance", "Saldo Total",
        device_class=SensorDeviceClass.MONETARY, unit="BRL", icon="mdi:bank"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "accounts", "summary.0.account_count", "Quantidade de Contas", icon="mdi:bank"
    ))

    # Endpoint Credit Cards: um sensor por cartão + sensores de resumo, no dispositivo "Cartões de Crédito"
    # Criar um sensor para cada cartão de crédito
    for card in cards_data.get("cards", []):
        entities.append(AbacoFinanceCreditCardSensor(client, entry, card))

    # Credit Cards summary sensors
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "credit_cards", "total_cards", "Total de Cartões", icon="mdi:credit-card-multiple"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "credit_cards", "total_limit", "Limite Total",
        device_class=SensorDeviceClass.MONETARY, unit="BRL"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "credit_cards", "total_used", "Usado Total",
        device_class=SensorDeviceClass.MONETARY, unit="BRL"
    ))
    entities.append(AbacoFinanceEndpointSensor(
        client, entry, "credit_cards", "total_available", "Disponível Total",
        device_class=SensorDeviceClass.MONETARY, unit="BRL"
    ))

    # Endpoint Investments: um sensor por investimento + sensor de valor total, no dispositivo "Investimentos"
    # Criar um sensor para cada investimento
    for investment in investments_data if isinstance(investments_data, list) else []:
        entities.append(AbacoFinanceInvestmentSensor(client, entry, investment))

    # Investments total sensor
    entities.append(AbacoFinanceInvestmentsTotalSensor(client, entry))

    # Endpoint Patrimony:
    # - Um sensor por patrimônio individual (data[])
    # - Um sensor de resumo total (summary.total_value)
    if isinstance(patrimony_data, dict) and patrimony_data:
        data_list = patrimony_data.get("data") or []
        if isinstance(data_list, list):
            for item in data_list:
                entities.append(AbacoFinancePatrimonyItemSensor(client, entry, item))

        summary = patrimony_data.get("summary") or {}
        if isinstance(summary, dict) and summary:
            entities.append(AbacoFinancePatrimonySummarySensor(client, entry, summary))

    async_add_entities(entities, True)


class AbacoFinanceEndpointSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para um atributo específico de um endpoint."""

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        endpoint: str,
        attribute_path: str,
        name: str,
        device_class: SensorDeviceClass | None = None,
        unit: str | None = None,
        icon: str | None = None,
    ) -> None:
        """Inicializa o sensor de endpoint."""
        super().__init__(client, entry)
        self._endpoint = endpoint
        self._attribute_path = attribute_path
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{endpoint}_{attribute_path.replace('.', '_')}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        if icon:
            self._attr_icon = icon

        # Mapeia nomes de endpoints para nomes amigáveis
        self._endpoint_names = {
            "profile": "Perfil",
            "accounts": "Contas",
            "credit_cards": "Cartões de Crédito",
            "investments": "Investimentos",
            "assets": "Ativos",
            "transactions": "Transações",
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Retorna as informações do dispositivo para este endpoint."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_{self._endpoint}")},
            name=self._endpoint_names.get(self._endpoint, self._endpoint.title()),
            manufacturer="Ábaco Finance",
            model=f"Endpoint - {self._endpoint}",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    def _get_nested_value(self, data: dict | list, path: str) -> Any:
        """Obtém valor de dict/list aninhado usando notação de pontos."""
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                try:
                    index = int(key)
                    value = value[index] if index < len(value) else None
                except (ValueError, IndexError):
                    value = None
            else:
                value = None
            
            if value is None:
                break
        
        return value

    async def _abaco_update(self) -> None:
        """Atualiza o valor do sensor."""
        # Buscar dados do endpoint apropriado
        if self._endpoint == "profile":
            data = await self.client.get_profile()
        elif self._endpoint == "accounts":
            data = await self.client.get_accounts()
        elif self._endpoint == "credit_cards":
            data = await self.client.get_credit_cards()
        elif self._endpoint == "investments":
            data = await self.client.get_investments()
        elif self._endpoint == "assets":
            data = await self.client.get_assets()
        elif self._endpoint == "transactions":
            data = await self.client.get_transactions()
        else:
            data = {}

        # Extract value using attribute path
        value = self._get_nested_value(data, self._attribute_path)
        
        # Convert to appropriate type
        if self._attr_device_class == SensorDeviceClass.MONETARY and value is not None:
            try:
                self._attr_native_value = float(value)
            except (ValueError, TypeError):
                self._attr_native_value = 0.0
        else:
            self._attr_native_value = value

        # Armazena os dados completos do endpoint em atributos
        self._attr_extra_state_attributes = {"endpoint_data": data}


class AbacoFinanceAccountSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para conta individual.

    Um sensor por conta:
    - nome = nome da conta
    - estado = current_balance
    - atributos = apenas os campos desta conta
    """

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        account: dict[str, Any],
    ) -> None:
        """Inicializa o sensor de conta."""
        super().__init__(client, entry)
        self._account_id = account["id"]
        self._account_name = account["name"]

        # Entity name = account name
        self._attr_name = self._account_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_account_{self._account_id}"
        self._attr_icon = "mdi:bank"

        # Estado = current_balance; atributos = apenas desta conta
        try:
            self._attr_native_value = float(account.get("current_balance", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = account

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os sensores de conta no dispositivo único 'Contas'."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_accounts")},
            name="Contas",
            manufacturer="Ábaco Finance",
            model="Endpoint - accounts",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Atualiza este sensor de conta apenas com seus próprios atributos."""
        data = await self.client.get_accounts()
        if not isinstance(data, dict):
            return

        for account in data.get("accounts", []):
            if account.get("id") == self._account_id:
                try:
                    self._attr_native_value = float(account.get("current_balance", 0))
                except (ValueError, TypeError):
                    self._attr_native_value = 0.0

                self._attr_extra_state_attributes = account
                return


class AbacoFinancePatrimonyItemSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para um patrimônio individual (item em patrimony.data)."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        item: dict[str, Any],
    ) -> None:
        """Inicializa o sensor de patrimônio individual."""
        super().__init__(client, entry)
        self._item_id = item["id"]
        self._item_name = item.get("name", "Patrimônio")
        self._patrimony_type = item.get("patrimony_type")
        self._patrimony_category = item.get("patrimony_category")

        # Nome da entidade = nome do patrimônio (ex: "S10 Rodeio", "Terreno")
        self._attr_name = self._item_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_patrimony_item_{self._item_id}"

        # Ícone baseado no tipo/categoria
        icon = "mdi:home"
        if self._patrimony_type == "vehicle":
            icon = "mdi:car"
        if self._patrimony_type == "property":
            icon = "mdi:home-city"
        if self._patrimony_category == "land":
            icon = "mdi:pine-tree"
        self._attr_icon = icon

        # Estado = current_value
        try:
            self._attr_native_value = float(item.get("current_value", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        # Atributos = somente este item
        self._attr_extra_state_attributes = item

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os patrimônios individuais em um único dispositivo 'Patrimônio'."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_patrimony")},
            name="Patrimônio",
            manufacturer="Ábaco Finance",
            model="Endpoint - patrimony",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Atualiza este patrimônio individual com base na lista patrimony.data."""
        data = await self.client.get_patrimony()
        if not isinstance(data, dict):
            return

        items = data.get("data") or []
        if not isinstance(items, list):
            return

        for item in items:
            if item.get("id") == self._item_id:
                try:
                    self._attr_native_value = float(item.get("current_value", 0))
                except (ValueError, TypeError):
                    self._attr_native_value = 0.0

                self._attr_extra_state_attributes = item
                return


class AbacoFinancePatrimonySummarySensor(AbacoFinanceEntity, SensorEntity):
    """Sensor de resumo de patrimônio (summary)."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"
    _attr_icon = "mdi:scale-balance"

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        summary: dict[str, Any],
    ) -> None:
        """Inicializa o sensor de resumo de patrimônio."""
        super().__init__(client, entry)
        self._attr_name = "Resumo Patrimônio"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_patrimony_summary"

        # Estado = total_value, se disponível
        value = summary.get("total_value")
        try:
            self._attr_native_value = float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = summary

    @property
    def device_info(self) -> DeviceInfo:
        """Usa o mesmo dispositivo 'Patrimônio' para o resumo."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_patrimony")},
            name="Patrimônio",
            manufacturer="Ábaco Finance",
            model="Endpoint - patrimony",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Atualiza o resumo de patrimônio."""
        data = await self.client.get_patrimony()
        if not isinstance(data, dict):
            return

        summary = data.get("summary") or {}
        if not isinstance(summary, dict):
            return

        value = summary.get("total_value")
        try:
            self._attr_native_value = float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = summary


class AbacoFinanceInvestmentSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para investimento individual.

    Um sensor por investimento:
    - nome = nome do investimento
    - estado = current_value
    - atributos = apenas os campos deste investimento
    """

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        investment: dict[str, Any],
    ) -> None:
        """Inicializa o sensor de investimento."""
        super().__init__(client, entry)
        self._investment_id = investment["id"]
        self._investment_name = investment["name"]

        self._attr_name = self._investment_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_investment_{self._investment_id}"
        self._attr_icon = "mdi:chart-line"

        try:
            self._attr_native_value = float(investment.get("current_value", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        # Apenas este investimento nos atributos
        self._attr_extra_state_attributes = investment

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os sensores de investimento no dispositivo único 'Investimentos'."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_investments")},
            name="Investimentos",
            manufacturer="Ábaco Finance",
            model="Endpoint - investments",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Atualiza este sensor de investimento apenas com seus próprios atributos."""
        data = await self.client.get_investments()
        if not isinstance(data, list):
            return

        for investment in data:
            if investment.get("id") == self._investment_id:
                try:
                    self._attr_native_value = float(investment.get("current_value", 0))
                except (ValueError, TypeError):
                    self._attr_native_value = 0.0

                self._attr_extra_state_attributes = investment
                return


class AbacoFinanceInvestmentsTotalSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para valor total de investimentos."""

    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
    ) -> None:
        """Inicializa o sensor de valor total de investimentos."""
        super().__init__(client, entry)
        self._attr_name = "Valor Total"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_investments_total_value"
        self._attr_native_unit_of_measurement = "BRL"
        self._attr_icon = "mdi:chart-line"

    @property
    def device_info(self) -> DeviceInfo:
        """Retorna as informações do dispositivo de investimentos."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_investments")},
            name="Investimentos",
            manufacturer="Ábaco Finance",
            model="Endpoint - investments",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Atualiza o valor total investido."""
        data = await self.client.get_investments()

        total = 0.0
        if isinstance(data, list):
            for investment in data:
                try:
                    total += float(investment.get("current_value", 0))
                except (ValueError, TypeError):
                    pass

        self._attr_native_value = total
        self._attr_extra_state_attributes = {
            "count": len(data) if isinstance(data, list) else 0,
            "investments": data,
        }


class AbacoFinanceCreditCardSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para cartão de crédito individual.

    Um sensor por cartão:
    - nome da entidade = nome do cartão
    - estado = current_balance (fatura atual)
    - atributos = apenas os campos deste cartão retornados pela API
    """

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
        card: dict[str, Any],
    ) -> None:
        """Inicializa o sensor de cartão de crédito."""
        super().__init__(client, entry)
        self._card_id = card["id"]
        self._card_name = card["name"]

        # Nome da entidade é exatamente o nome do cartão
        self._attr_name = self._card_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_card_{self._card_id}"
        self._attr_icon = "mdi:credit-card"

        # Estado = current_balance; atributos = apenas deste cartão
        try:
            self._attr_native_value = float(card.get("current_balance", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = card

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information.

        All credit card sensors are grouped under a single
        'Cartões de Crédito' device.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_credit_cards")},
            name="Cartões de Crédito",
            manufacturer="Ábaco Finance",
            model="Endpoint - credit_cards",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def _abaco_update(self) -> None:
        """Update this card sensor with its specific attributes only."""
        data = await self.client.get_credit_cards()
        if not isinstance(data, dict):
            return

        for card in data.get("cards", []):
            if card.get("id") == self._card_id:
                # Update state with this card's current_balance
                try:
                    self._attr_native_value = float(card.get("current_balance", 0))
                except (ValueError, TypeError):
                    self._attr_native_value = 0.0

                # Attributes = only this card object
                self._attr_extra_state_attributes = card
                return
