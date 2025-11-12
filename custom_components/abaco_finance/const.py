"""Constants for the Ábaco Finance integration."""

import logging

DOMAIN = "abaco_finance"

LOGGER = logging.getLogger(__package__)

# Configuration
CONF_API_URL = "api_url"
CONF_API_TOKEN = "api_token"

# Default values
DEFAULT_API_URL = "https://api.abacofinance.com.br"

# API Endpoints
ENDPOINT_PROFILE = "/api/v1/profile"
ENDPOINT_TRANSACTIONS = "/api/v1/transactions"
ENDPOINT_ACCOUNTS = "/api/v1/accounts"
ENDPOINT_CREDIT_CARDS = "/api/v1/credit-cards"
ENDPOINT_INVESTMENTS = "/api/v1/investments"
ENDPOINT_ASSETS = "/api/v1/assets"
