from enum import Enum

# Definiamo l'Enum per il tipo di rete
class TipoRete(Enum):
    LOCALE = "Locale"
    VPN = "VPN"
    PUBBLICA = "Pubblica"