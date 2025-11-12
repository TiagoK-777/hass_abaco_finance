# Ábaco Finance - Integração para Home Assistant

Integração customizada para o Home Assistant que consome a API do Ábaco Finance e expõe sensores para monitorar seu patrimônio financeiro.

Este repositório está preparado para ser utilizado como repositório custom do HACS.

## Recursos

A integração cria sensores (principalmente monetários) baseados nos dados retornados pela API do Ábaco Finance, incluindo (conforme implementação atual):

- Perfil do usuário
- Contas bancárias
- Cartões de crédito
- Investimentos
- Patrimônio (itens e resumo)
- Ativos
- Transações

Os dados são obtidos via API utilizando token de autenticação informado pelo usuário.

## Instalação via HACS

1. No Home Assistant, acesse:
   - HACS > Integrations > Custom repositories
2. Em "Add custom repository", informe:
   - URL: `https://github.com/TiagoK-777/hass-abaco-finance`
   - Category: `Integration`
3. Clique em "Add".
4. Ainda no HACS, procure por:
   - `Ábaco Finance`
5. Instale a integração.
6. Reinicie o Home Assistant se necessário.

## Configuração

A configuração é feita via interface (Config Flow):

1. Acesse:
   - Settings > Devices & Services > Add Integration.
2. Busque por:
   - `Ábaco Finance`.
3. Informe:
   - URL da API (padrão: `https://api.abacofinance.com.br`)
   - Token da API

A integração validará o token e conectividade antes de criar a entrada.

## Estrutura do Repositório

```text
.
├── abaco_finance/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config_flow.py
│   ├── const.py
│   ├── entity.py
│   ├── manifest.json
│   ├── sensor.py
│   ├── strings.json
│   ├── icons.json
│   ├── icon.png
│   └── logo.png
├── .github/
│   └── workflows/
│       └── validate_abaco_finance.yml
├── hacs.json
├── LICENSE
└── README.md
```

## Suporte HACS

Este repositório é compatível com HACS através do arquivo `hacs.json`, apontando para o domínio `abaco_finance`.

## Links

- Documentação: https://github.com/TiagoK-777/hass-abaco-finance
- Issues: https://github.com/TiagoK-777/hass-abaco-finance/issues

## Aviso

Esta integração não é oficial do Ábaco Finance. Utilize por sua conta e risco e mantenha seu token de API em segurança.