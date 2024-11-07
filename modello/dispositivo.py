class Dispositivo:
    def __init__(self, ip, mac, tipoDispositivo, so, nomeHost, tempoRisposta, ttl, stato, porteAperte=None,
                 serviziAttivi=None):
        self._ip = ip
        self._mac = mac
        self._tipoDispositivo = tipoDispositivo
        self._so = so
        self._nomeHost = nomeHost
        self._tempoRisposta = tempoRisposta
        self._ttl = ttl
        self._stato = stato
        # Porte aperte: una lista, se non fornita è una lista vuota
        self._porteAperte = porteAperte if porteAperte is not None else []
        # Servizi attivi: un dizionario (porta: servizio), se non fornito è un dizionario vuoto
        self._serviziAttivi = serviziAttivi if serviziAttivi is not None else {}

    # Getter e Setter per l'attributo 'ip'
    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    # Getter e Setter per l'attributo 'mac'
    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value):
        self._mac = value

    # Getter e Setter per l'attributo 'tipoDispositivo'
    @property
    def tipoDispositivo(self):
        return self._tipoDispositivo

    @tipoDispositivo.setter
    def tipoDispositivo(self, value):
        self._tipoDispositivo = value

    # Getter e Setter per l'attributo 'so' (sistema operativo)
    @property
    def so(self):
        return self._so

    @so.setter
    def so(self, value):
        self._so = value

    # Getter e Setter per l'attributo 'nomeHost'
    @property
    def nomeHost(self):
        return self._nomeHost

    @nomeHost.setter
    def nomeHost(self, value):
        self._nomeHost = value

    # Getter e Setter per l'attributo 'tempoRisposta'
    @property
    def tempoRisposta(self):
        return self._tempoRisposta

    @tempoRisposta.setter
    def tempoRisposta(self, value):
        if value < 0:
            raise ValueError("Il tempo di risposta non può essere negativo.")
        self._tempoRisposta = value

    # Getter e Setter per l'attributo 'ttl'
    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

    # Getter e Setter per l'attributo 'stato'
    @property
    def stato(self):
        return self._stato

    @stato.setter
    def stato(self, value):
        if value not in ["Attivo", "Inattivo"]:
            raise ValueError("Stato non valido. Deve essere 'Attivo' o 'Inattivo'.")
        self._stato = value

    # Getter e Setter per l'attributo 'porteAperte'
    @property
    def porteAperte(self):
        return self._porteAperte

    @porteAperte.setter
    def porteAperte(self, value):
        if not isinstance(value, list):
            raise TypeError("Le porte aperte devono essere una lista.")
        self._porteAperte = value

    # Getter e Setter per l'attributo 'serviziAttivi'
    @property
    def serviziAttivi(self):
        return self._serviziAttivi

    @serviziAttivi.setter
    def serviziAttivi(self, value):
        if not isinstance(value, dict):
            raise TypeError("I servizi attivi devono essere un dizionario con chiave porta e valore servizio.")
        self._serviziAttivi = value

    def aggiungi_servizio(self, porta, servizio):
        """
        Aggiunge un servizio alla mappa dei servizi attivi, associandolo alla porta.
        """
        if not isinstance(porta, int) or not isinstance(servizio, str):
            raise ValueError("La porta deve essere un intero e il servizio deve essere una stringa.")
        self._serviziAttivi[porta] = servizio

    def rimuovi_servizio(self, porta):
        """
        Rimuove il servizio associato alla determinata porta.
        """
        if porta in self._serviziAttivi:
            del self._serviziAttivi[porta]
        else:
            raise KeyError(f"Porta {porta} non trovata nei servizi attivi.")

    def __str__(self):
        return (f"Dispositivo(ip={self._ip}, mac={self._mac}, tipoDispositivo={self._tipoDispositivo}, "
                f"so={self._so}, nomeHost={self._nomeHost}, tempoRisposta={self._tempoRisposta}, "
                f"ttl={self._ttl}, stato={self._stato}, porteAperte={self._porteAperte}, "
                f"serviziAttivi={self._serviziAttivi})")
