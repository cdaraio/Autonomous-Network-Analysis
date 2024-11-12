from enum import Enum
from typing import List, Dict, Optional

# Definiamo l'Enum per il tipo di dispositivo
class TipoDispositivo(Enum):
    CLIENT = "Client"
    SERVER = "Server"
    UNKNOWN = "Sconosciuto"

class Dispositivo:
    def __init__(self, ip: Optional[str] = None, mac: Optional[str] = None, tipo_dispositivo: Optional[TipoDispositivo] = TipoDispositivo.UNKNOWN,
                 so: Optional[str] = None, nome_host: Optional[str] = None, tempo_risposta: float = 0.0,
                 ttl: float = 0.0, stato: Optional[str] = None):
        self._ip = ip
        self._mac = mac
        self._tipo_dispositivo = tipo_dispositivo  # Presuppone che tipo_dispositivo sia un'istanza dell'Enum TipoDispositivo
        self._so = so
        self._nome_host = nome_host
        self._tempo_risposta = tempo_risposta
        self._ttl = ttl
        self._stato = stato
        self._porte_aperte: List[int] = []
        self._servizi_attivi: Dict[int, str] = {}

    # Proprietà per IP
    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    # Proprietà per MAC
    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value):
        self._mac = value

    # Proprietà per TipoDispositivo
    @property
    def tipo_dispositivo(self):
        return self._tipo_dispositivo

    @tipo_dispositivo.setter
    def tipo_dispositivo(self, value):
        if isinstance(value, TipoDispositivo):
            self._tipo_dispositivo = value
        else:
            raise ValueError(f"Tipo di dispositivo non valido: {value}")

    # Proprietà per SO
    @property
    def so(self):
        return self._so

    @so.setter
    def so(self, value):
        self._so = value

    # Proprietà per NomeHost
    @property
    def nome_host(self):
        return self._nome_host

    @nome_host.setter
    def nome_host(self, value):
        self._nome_host = value

    # Proprietà per TempoRisposta
    @property
    def tempo_risposta(self):
        return self._tempo_risposta

    @tempo_risposta.setter
    def tempo_risposta(self, value):
        self._tempo_risposta = value

    # Proprietà per TTL
    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

    # Proprietà per Stato
    @property
    def stato(self):
        return self._stato

    @stato.setter
    def stato(self, value):
        self._stato = value

    # Metodi per PorteAperte
    @property
    def porte_aperte(self):
        return self._porte_aperte

    def aggiungi_porta_aperta(self, porta: int):
        self._porte_aperte.append(porta)

    # Metodi per ServiziAttivi
    @property
    def servizi_attivi(self):
        return self._servizi_attivi

    def aggiungi_servizio_attivo(self, chiave: int, valore: str):
        self._servizi_attivi[chiave] = valore

    def get_servizio_attivo(self, chiave: int):
        return self._servizi_attivi.get(chiave)

    # Metodo __str__ per rappresentazione leggibile
    def __str__(self):
        return (f"Dispositivo(ip={self._ip}, mac={self._mac}, tipo_dispositivo={self._tipo_dispositivo}, "
                f"so={self._so}, nome_host={self._nome_host}, tempo_risposta={self._tempo_risposta}, "
                f"ttl={self._ttl}, stato={self._stato}, porte_aperte={self._porte_aperte}, "
                f"servizi_attivi={self._servizi_attivi})")
