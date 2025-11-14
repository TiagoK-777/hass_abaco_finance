"""
Mapeamento completo de emojis para ícones MDI do Home Assistant.
Baseado na biblioteca Material Design Icons (MDI).
"""

# ========================================
# PATRIMÔNIO - CATEGORIAS PRINCIPAIS
# ========================================
PATRIMONIO_ICONS = {
    # Imóveis
    '🏠': 'mdi:home',
    '🏢': 'mdi:office-building',
    '🏘️': 'mdi:home-group',
    '🏰': 'mdi:castle',
    '🏞️': 'mdi:image-filter-hdr',
    '🏭': 'mdi:factory',
    
    # Veículos
    '🚗': 'mdi:car',
    '🏍️': 'mdi:motorbike',
    '🚚': 'mdi:truck',
    '🚐': 'mdi:van-utility',
    '🚌': 'mdi:bus',
    '⛵': 'mdi:sail-boat',
    '🛥️': 'mdi:ferry',
    '✈️': 'mdi:airplane',
    '🚁': 'mdi:helicopter',
    '🚲': 'mdi:bike',
    
    # Eletrônicos & Tecnologia
    '💻': 'mdi:laptop',
    '📱': 'mdi:cellphone',
    '📷': 'mdi:camera',
    '⌚': 'mdi:watch',
    '📺': 'mdi:television',
    '🖥️': 'mdi:monitor',
    
    # Joias & Acessórios
    '💎': 'mdi:diamond-stone',
    '💍': 'mdi:ring',
    '👑': 'mdi:crown',
    '💠': 'mdi:diamond',
    
    # Arte & Colecionáveis
    '🎨': 'mdi:palette',
    '🖼️': 'mdi:image-frame',
    '🏆': 'mdi:trophy',
    '🏅': 'mdi:medal',
    
    # Outros
    '📦': 'mdi:package-variant-closed',
    '💼': 'mdi:briefcase',
    '🛠️': 'mdi:tools',
    '🪑': 'mdi:chair-rolling',
    '🌱': 'mdi:sprout',
    '🐕': 'mdi:dog',
}

# ========================================
# INVESTIMENTOS - TIPOS
# ========================================
INVESTMENT_ICONS = {
    '📈': 'mdi:chart-line',           # Ações
    '🏢': 'mdi:office-building',      # FII
    '₿': 'mdi:currency-btc',          # Criptomoedas
    '🧾': 'mdi:receipt-text',         # Renda Fixa
    '💼': 'mdi:briefcase',            # Fundos
    '🤝': 'mdi:handshake',            # Participação
    '🥇': 'mdi:medal',                # Ouro
    '🐷': 'mdi:piggy-bank',           # Poupança
    '📜': 'mdi:file-document',        # Títulos
    '📊': 'mdi:chart-bar',            # ETFs
}

# ========================================
# CONTAS - TIPOS
# ========================================
ACCOUNT_ICONS = {
    '💳': 'mdi:credit-card',          # Corrente
    '🐷': 'mdi:piggy-bank',           # Poupança
    '📊': 'mdi:chart-line',           # Investimento
    '👛': 'mdi:wallet',               # Carteira
    '📱': 'mdi:cellphone',            # Conta Digital
}

# ========================================
# CARTÕES - STATUS
# ========================================
CARD_ICONS = {
    '✅': 'mdi:check-circle',         # Ativo
    '❌': 'mdi:close-circle',         # Inativo
    '💳': 'mdi:credit-card',          # Crédito/Débito
    '🔴': 'mdi:circle',               # Mastercard
    '🔵': 'mdi:circle',               # Visa
    '🔷': 'mdi:rhombus',              # American Express
    '🟡': 'mdi:circle',               # Elo
}

# ========================================
# CATEGORIAS DE TRANSAÇÕES
# ========================================
TRANSACTION_CATEGORY_ICONS = {
    # Alimentação
    '🍔': 'mdi:hamburger',
    '🍽️': 'mdi:silverware-fork-knife',
    '🛒': 'mdi:cart',
    '☕': 'mdi:coffee',
    '🍕': 'mdi:pizza',
    
    # Transporte
    '🚗': 'mdi:car',
    '⛽': 'mdi:gas-station',
    '🅿️': 'mdi:parking',
    '🚕': 'mdi:taxi',
    '🚇': 'mdi:subway-variant',
    
    # Moradia
    '🏠': 'mdi:home',
    '🏘️': 'mdi:home-group',
    '💡': 'mdi:lightbulb',
    '💧': 'mdi:water',
    '📡': 'mdi:wifi',
    '📞': 'mdi:phone',
    
    # Saúde
    '🏥': 'mdi:hospital-building',
    '💊': 'mdi:pill',
    '👨‍⚕️': 'mdi:doctor',
    '💪': 'mdi:dumbbell',
    
    # Educação
    '📚': 'mdi:book-open-page-variant',
    '🎓': 'mdi:school',
    '📖': 'mdi:book-open',
    
    # Entretenimento
    '🎬': 'mdi:movie-open',
    '🎥': 'mdi:movie',
    '🎵': 'mdi:music',
    '🎮': 'mdi:gamepad-variant',
    '✈️': 'mdi:airplane',
    '🏨': 'mdi:hotel',
    
    # Compras
    '🛍️': 'mdi:shopping',
    '👔': 'mdi:tshirt-crew',
    '👟': 'mdi:shoe-sneaker',
    '📱': 'mdi:cellphone',
    
    # Finanças
    '🏦': 'mdi:bank',
    '📈': 'mdi:chart-line',
    '💰': 'mdi:currency-usd',
    '💳': 'mdi:credit-card',
    
    # Trabalho
    '💵': 'mdi:cash',
    '🎁': 'mdi:gift',
    '💼': 'mdi:briefcase',
    
    # Outros
    '❤️': 'mdi:heart',
    '🐾': 'mdi:paw',
    '💄': 'mdi:lipstick',
    '📦': 'mdi:package-variant-closed',
}

# ========================================
# ÍCONES GERAIS DA APLICAÇÃO
# ========================================
APP_ICONS = {
    # Navegação
    '📊': 'mdi:view-dashboard',
    '💸': 'mdi:cash-multiple',
    '🏦': 'mdi:bank',
    '💳': 'mdi:credit-card',
    '📈': 'mdi:chart-line',
    '🏠': 'mdi:home',
    '📋': 'mdi:file-document',
    '⚙️': 'mdi:cog',
    
    # Ações
    '➕': 'mdi:plus',
    '✏️': 'mdi:pencil',
    '🗑️': 'mdi:delete',
    '💾': 'mdi:content-save',
    '❌': 'mdi:close',
    '✅': 'mdi:check',
    '🔍': 'mdi:magnify',
    '🔽': 'mdi:filter',
    '↕️': 'mdi:sort',
    
    # Status
    '⚠️': 'mdi:alert',
    'ℹ️': 'mdi:information',
    '⏳': 'mdi:clock-outline',
    
    # Moedas
    '💵': 'mdi:currency-usd',
    '💶': 'mdi:currency-eur',
    
    # Diversos
    '👤': 'mdi:account',
    '🚪': 'mdi:logout',
    '❓': 'mdi:help-circle',
    '🔔': 'mdi:bell',
    '📅': 'mdi:calendar',
    '📄': 'mdi:file-document',
    '🔒': 'mdi:lock',
    '🔓': 'mdi:lock-open',
}

# ========================================
# DICIONÁRIO UNIFICADO
# ========================================
EMOJI_TO_MDI = {
    **PATRIMONIO_ICONS,
    **INVESTMENT_ICONS,
    **ACCOUNT_ICONS,
    **CARD_ICONS,
    **TRANSACTION_CATEGORY_ICONS,
    **APP_ICONS,
}

# ========================================
# FUNÇÕES HELPER
# ========================================

def get_mdi_icon(emoji: str, default: str = 'mdi:package-variant-closed') -> str:
    """
    Retorna o ícone MDI correspondente ao emoji.
    
    Args:
        emoji: Emoji para converter
        default: Ícone padrão se não encontrar correspondência
        
    Returns:
        String com o nome do ícone MDI (ex: 'mdi:home')
    """
    return EMOJI_TO_MDI.get(emoji, default)

def get_all_supported_emojis() -> list[str]:
    """Retorna lista de todos os emojis suportados."""
    return list(EMOJI_TO_MDI.keys())

def get_icons_by_category(category: str) -> dict[str, str]:
    """
    Retorna ícones de uma categoria específica.
    
    Args:
        category: 'patrimonio', 'investment', 'account', 'card', 'transaction', 'app'
        
    Returns:
        Dicionário com mapeamento emoji -> mdi
    """
    categories = {
        'patrimonio': PATRIMONIO_ICONS,
        'investment': INVESTMENT_ICONS,
        'account': ACCOUNT_ICONS,
        'card': CARD_ICONS,
        'transaction': TRANSACTION_CATEGORY_ICONS,
        'app': APP_ICONS,
    }
    return categories.get(category.lower(), {})

def is_emoji_supported(emoji: str) -> bool:
    """Verifica se um emoji tem mapeamento MDI."""
    return emoji in EMOJI_TO_MDI
