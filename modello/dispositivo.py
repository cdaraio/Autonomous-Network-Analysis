from typing import List, Dict, Optional

class Dispositivo:
    def __init__(self, ip, mac, tipologia, so, nome_host, tempo_risposta, ttl, stato, servizi_attivi=None):
        self.ip = ip
        self.mac = mac
        self.tipologia = tipologia
        self.so = so
        self.nome_host = nome_host
        self.tempo_risposta = tempo_risposta
        self.ttl = ttl
        self.stato = stato
        # Inizializza i servizi attivi come dizionario vuoto se non fornito
        self._servizi_attivi = servizi_attivi if servizi_attivi is not None else {}

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

    @property
    def tipologia(self):
        return self._tipologia

    @tipologia.setter
    def tipologia(self, value):
        self._tipologia = value

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
        return (f"Dispositivo(ip={self._ip}, mac={self._mac}, "
                f"so={self._so}, nome_host={self._nome_host}, nome_host={self._nome_host}, tipologia={self.tipologia}, tempo_risposta={self._tempo_risposta}, "
                f"ttl={self._ttl}, stato={self._stato}, "
                f"servizi_attivi={self._servizi_attivi})")
