from modello.subnet import Subnet


class Rete:
        def __init__(self, subnet=None):
            self._subnet = subnet if subnet else []

        def aggiungi_subnet(self, subnet):
            if isinstance(subnet, Subnet):
                self._subnet.append(subnet)
            else:
                raise TypeError("Deve essere un oggetto di tipo 'Subnet'")