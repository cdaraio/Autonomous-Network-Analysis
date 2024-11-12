from typing import Any, Dict

class Modello:
    def __init__(self):
        self._beans: Dict[str, Any] = {}

    def aggiungi_bean(self, chiave: str, valore: Any):
        self._beans[chiave] = valore

    def ottieni_bean(self, chiave: str) -> Any:
        return self._beans.get(chiave)
