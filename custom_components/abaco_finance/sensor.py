"""Suporte para sensores do Ábaco Finance."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
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
    client: AbacoFinanceClient = entry.runtime_data
    entities: list[SensorEntity] = []

    # Buscar dados iniciais para criar sensores dinamicamente
    # Busca cada endpoint individualmente para não quebrar tudo se um falhar
    from .const import LOGGER
    
    # Cartões de crédito
    try:
        cards_data = await client.get_credit_cards()
        LOGGER.info("Dados de cartões obtidos com sucesso: %d cartões", len(cards_data.get("cards", [])) if isinstance(cards_data, dict) else 0)
    except Exception as e:
        LOGGER.warning("Erro ao buscar cartões de crédito: %s", e)
        cards_data = {"cards": []}
    
    # Contas
    try:
        accounts_data = await client.get_accounts()
        LOGGER.info("Dados de contas obtidos com sucesso: %d contas", len(accounts_data.get("accounts", [])) if isinstance(accounts_data, dict) else 0)
    except Exception as e:
        LOGGER.warning("Erro ao buscar contas: %s", e)
        accounts_data = {"accounts": []}
    
    # Investimentos
    try:
        investments_data = await client.get_investments()
        LOGGER.info("Dados de investimentos obtidos com sucesso: %d investimentos", len(investments_data) if isinstance(investments_data, list) else 0)
    except Exception as e:
        LOGGER.warning("Erro ao buscar investimentos: %s", e)
        investments_data = []
    
    # Patrimônio
    try:
        patrimony_data = await client.get_patrimony()
        LOGGER.info("Dados de patrimônio obtidos com sucesso")
    except Exception as e:
        LOGGER.warning("Erro ao buscar patrimônio: %s", e)
        patrimony_data = {}

    # =========================
    # Endpoint Profile - sensores fixos
    # =========================
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "profile",
            "name",
            "Nome",
            icon="mdi:account",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "profile",
            "email",
            "Email",
            icon="mdi:email",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "profile",
            "default_currency",
            "Moeda Padrão",
            icon="mdi:currency-usd",
        )
    )

    # =========================
    # Endpoint Accounts
    # - Um sensor por conta
    # - Sensores de resumo no mesmo dispositivo "Contas"
    # =========================

    # Um sensor por conta
    if isinstance(accounts_data, dict):
        accounts_list = accounts_data.get("accounts", [])
        LOGGER.info("Criando %d sensores de contas", len(accounts_list))
        for account in accounts_list:
            if isinstance(account, dict) and "id" in account and "name" in account:
                LOGGER.info("Criando sensor para conta: %s (ID: %s)", account.get("name"), account.get("id"))
                entities.append(
                    AbacoFinanceAccountSensor(
                        client,
                        entry,
                        account,
                    )
                )
            else:
                LOGGER.warning("Conta inválida ignorada: %s", account)

    # Sensores de resumo
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "accounts",
            "total_accounts",
            "Total de Contas",
            icon="mdi:counter",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "accounts",
            "summary.0.total_balance",
            "Saldo Total",
            device_class=SensorDeviceClass.MONETARY,
            unit="BRL",
            icon="mdi:bank",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "accounts",
            "summary.0.account_count",
            "Quantidade de Contas",
            icon="mdi:bank",
        )
    )

    # =========================
    # Endpoint Credit Cards
    # - Um sensor por cartão
    # - Sensores de resumo no dispositivo "Cartões de Crédito"
    # =========================

    if isinstance(cards_data, dict):
        cards_list = cards_data.get("cards", [])
        LOGGER.info("Criando %d sensores de cartões de crédito", len(cards_list))
        for card in cards_list:
            if isinstance(card, dict) and "id" in card and "name" in card:
                LOGGER.info("Criando sensor para cartão: %s (ID: %s)", card.get("name"), card.get("id"))
                entities.append(
                    AbacoFinanceCreditCardSensor(
                        client,
                        entry,
                        card,
                    )
                )
            else:
                LOGGER.warning("Cartão inválido ignorado: %s", card)

    # Sensores de resumo de cartões
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "credit_cards",
            "total_cards",
            "Total de Cartões",
            icon="mdi:credit-card-multiple",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "credit_cards",
            "total_limit",
            "Limite Total",
            device_class=SensorDeviceClass.MONETARY,
            unit="BRL",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "credit_cards",
            "total_used",
            "Usado Total",
            device_class=SensorDeviceClass.MONETARY,
            unit="BRL",
        )
    )
    entities.append(
        AbacoFinanceEndpointSensor(
            client,
            entry,
            "credit_cards",
            "total_available",
            "Disponível Total",
            device_class=SensorDeviceClass.MONETARY,
            unit="BRL",
        )
    )

    # =========================
    # Endpoint Investments
    # - Um sensor por investimento
    # - Um sensor para o valor total
    # =========================

    if isinstance(investments_data, list):
        LOGGER.info("Criando %d sensores de investimentos", len(investments_data))
        for investment in investments_data:
            if isinstance(investment, dict) and "id" in investment and "name" in investment:
                LOGGER.info("Criando sensor para investimento: %s (ID: %s)", investment.get("name"), investment.get("id"))
                entities.append(
                    AbacoFinanceInvestmentSensor(
                        client,
                        entry,
                        investment,
                    )
                )
            else:
                LOGGER.warning("Investimento inválido ignorado: %s", investment)

    entities.append(
        AbacoFinanceInvestmentsTotalSensor(
            client,
            entry,
        )
    )

    # =========================
    # Endpoint Patrimony
    # - Um sensor por patrimônio individual (data[])
    # - Um sensor de resumo (summary.total_value)
    # =========================

    if isinstance(patrimony_data, dict) and patrimony_data:
        data_list = patrimony_data.get("data") or []
        if isinstance(data_list, list):
            LOGGER.info("Criando %d sensores de patrimônio", len(data_list))
            for item in data_list:
                if isinstance(item, dict) and "id" in item:
                    LOGGER.info("Criando sensor para patrimônio: %s (ID: %s)", item.get("name", "Sem nome"), item.get("id"))
                    entities.append(
                        AbacoFinancePatrimonyItemSensor(
                            client,
                            entry,
                            item,
                        )
                    )
                else:
                    LOGGER.warning("Item de patrimônio inválido ignorado: %s", item)

        summary = patrimony_data.get("summary") or {}
        if isinstance(summary, dict) and summary:
            entities.append(
                AbacoFinancePatrimonySummarySensor(
                    client,
                    entry,
                    summary,
                )
            )

    # Registrar todas as entidades
    LOGGER.info("Total de entidades criadas: %d", len(entities))
    async_add_entities(entities, True)


class AbacoFinanceEndpointSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor genérico para um atributo específico de um endpoint."""

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
        self._attr_unique_id = (
            f"{DOMAIN}_{entry.entry_id}_{endpoint}_{attribute_path.replace('.', '_')}"
        )
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        if icon:
            self._attr_icon = icon

        # Nomes amigáveis por endpoint (para device_info)
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
        """Retorna as informações do dispositivo para este endpoint.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_{self._endpoint}")},
            name=self._endpoint_names.get(self._endpoint, self._endpoint.title()),
            manufacturer="Ábaco Finance",
            model=f"Endpoint - {self._endpoint}",
        )

    def _get_nested_value(self, data: dict | list, path: str) -> Any:
        """Obtém valor de dict/list aninhado usando notação de pontos."""
        keys = path.split(".")
        value: Any = data

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
        """Atualiza o valor do sensor a partir do endpoint configurado."""
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

        value = self._get_nested_value(data, self._attribute_path)

        if self._attr_device_class == SensorDeviceClass.MONETARY and value is not None:
            try:
                self._attr_native_value = float(value)
            except (ValueError, TypeError):
                self._attr_native_value = 0.0
        else:
            self._attr_native_value = value

        self._attr_extra_state_attributes = {"endpoint_data": data}


class AbacoFinanceAccountSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para conta individual."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"
    _attr_entity_registry_enabled_default = True

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

        self._attr_name = self._account_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_account_{self._account_id}"
        self._attr_icon = "mdi:bank"

        try:
            self._attr_native_value = float(account.get("current_balance", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = account

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os sensores de conta no dispositivo único 'Contas'.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_accounts")},
            name="Contas",
            manufacturer="Ábaco Finance",
            model="Endpoint - accounts",
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


class AbacoFinanceCreditCardSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para cartão de crédito individual."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"
    _attr_entity_registry_enabled_default = True

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

        self._attr_name = self._card_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_credit_card_{self._card_id}"
        self._attr_icon = "mdi:credit-card"

        try:
            self._attr_native_value = float(card.get("current_balance", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = card

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os sensores de cartão no dispositivo único 'Cartões de Crédito'.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_credit_cards")},
            name="Cartões de Crédito",
            manufacturer="Ábaco Finance",
            model="Endpoint - credit_cards",
        )

    async def _abaco_update(self) -> None:
        """Atualiza este sensor de cartão apenas com seus próprios atributos."""
        data = await self.client.get_credit_cards()
        if not isinstance(data, dict):
            return

        for card in data.get("cards", []):
            if card.get("id") == self._card_id:
                try:
                    self._attr_native_value = float(card.get("current_balance", 0))
                except (ValueError, TypeError):
                    self._attr_native_value = 0.0

                self._attr_extra_state_attributes = card
                return


class AbacoFinancePatrimonyItemSensor(AbacoFinanceEntity, SensorEntity):
    """Sensor para um patrimônio individual (item em patrimony.data)."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"
    _attr_entity_registry_enabled_default = True

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

        self._attr_name = self._item_name
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_patrimony_item_{self._item_id}"

        icon = "mdi:home"
        if self._patrimony_type == "vehicle":
            icon = "mdi:car"
        elif self._patrimony_type == "property":
            icon = "mdi:home-city"
        if self._patrimony_category == "land":
            icon = "mdi:pine-tree"
        self._attr_icon = icon

        try:
            self._attr_native_value = float(item.get("current_value", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = item

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os patrimônios individuais em um único dispositivo 'Patrimônio'.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_patrimony")},
            name="Patrimônio",
            manufacturer="Ábaco Finance",
            model="Endpoint - patrimony",
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

        value = summary.get("total_value")
        try:
            self._attr_native_value = float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = summary

    @property
    def device_info(self) -> DeviceInfo:
        """Usa o mesmo dispositivo 'Patrimônio' para o resumo.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_patrimony")},
            name="Patrimônio",
            manufacturer="Ábaco Finance",
            model="Endpoint - patrimony",
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
    """Sensor para investimento individual."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BRL"
    _attr_entity_registry_enabled_default = True

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
        self._attr_unique_id = (
            f"{DOMAIN}_{entry.entry_id}_investment_{self._investment_id}"
        )
        self._attr_icon = "mdi:chart-line"

        try:
            self._attr_native_value = float(investment.get("current_value", 0))
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        self._attr_extra_state_attributes = investment

    @property
    def device_info(self) -> DeviceInfo:
        """Agrupa todos os sensores de investimento no dispositivo único 'Investimentos'.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_investments")},
            name="Investimentos",
            manufacturer="Ábaco Finance",
            model="Endpoint - investments",
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
    _attr_native_unit_of_measurement = "BRL"
    _attr_icon = "mdi:chart-line"
    _attr_entity_registry_enabled_default = True

    def __init__(
        self,
        client: AbacoFinanceClient,
        entry: AbacoFinanceConfigEntry,
    ) -> None:
        """Inicializa o sensor de valor total de investimentos."""
        super().__init__(client, entry)
        self._attr_name = "Valor Total Investido"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_investments_total_value"

    @property
    def device_info(self) -> DeviceInfo:
        """Retorna as informações do dispositivo de investimentos.

        Não define via_device para evitar referência a dispositivo pai inexistente.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}_investments")},
            name="Investimentos",
            manufacturer="Ábaco Finance",
            model="Endpoint - investments",
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
                    continue

        self._attr_native_value = total
        self._attr_extra_state_attributes = {
            "count": len(data) if isinstance(data, list) else 0,
            "investments": data if isinstance(data, list) else [],
        }
