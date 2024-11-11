from typing import List
from modello.subnet import Subnet  # Importa la classe Subnet dal modulo appropriato

class Rete:
    def __init__(self):
        self._lista_subnet: List[Subnet] = []

    @property
    def lista_subnet(self) -> List[Subnet]:
        return self._lista_subnet

    def aggiungi_subnet(self, subnet: Subnet):
        self._lista_subnet.append(subnet)
