from modello.enum_rete import TipoRete


class Subnet:
    def __init__(self, indirizzo, maschera, tipo_rete, dispositivi=None, gateway=None):
        self._indirizzo = indirizzo
        self._maschera = maschera
        self._tipo_rete = TipoRete[tipo_rete] if isinstance(tipo_rete, str) else tipo_rete
        self._dispositivi = dispositivi if dispositivi is not None else []
        self._gateway = gateway

    # Getter e Setter per l'attributo 'indirizzo'
    @property
    def indirizzo(self):
        return self._indirizzo

    @indirizzo.setter
    def indirizzo(self, value):
        self._indirizzo = value

    # Getter e Setter per l'attributo 'maschera'
    @property
    def maschera(self):
        return self._maschera

    @maschera.setter
    def maschera(self, value):
        self._maschera = value

    # Getter e Setter per l'attributo 'tipo_rete' (utilizzando Enum)
    @property
    def tipo_rete(self):
        return self._tipo_rete.value

    @tipo_rete.setter
    def tipo_rete(self, value):
        if isinstance(value, str):
            self._tipo_rete = TipoRete[value]
        else:
            self._tipo_rete = value

    # Getter e Setter per l'attributo 'dispositivi'
    @property
    def dispositivi(self):
        return self._dispositivi

    @dispositivi.setter
    def dispositivi(self, value):
        if not isinstance(value, list):
            raise TypeError("I dispositivi devono essere una lista.")
        self._dispositivi = value

    # Getter e Setter per l'attributo 'gateway'
    @property
    def gateway(self):
        return self._gateway

    @gateway.setter
    def gateway(self, value):
        self._gateway = value

    def __str__(self):
        dispositivi_str = ', '.join([str(dispositivo.ip) for dispositivo in self._dispositivi])
        return (f"Subnet(indirizzo={self._indirizzo}, maschera={self._maschera}, "
                f"tipo_rete={self._tipo_rete.value}, dispositivi=[{dispositivi_str}], gateway={self._gateway})")

