from typing import Any, Dict
import logging

class Modello:
    def __init__(self):
        self._beans: Dict[str, Any] = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def aggiungi_bean(self, chiave: str, valore: Any):
        self._beans[chiave] = valore
        self.log_mappa_lunghezza()

        if isinstance(valore, list):
            self.logger.info(f"Lunghezza della lista di dispositivi: {len(valore)}")

    def ottieni_bean(self, chiave: str) -> Any:
        valore = self._beans.get(chiave)
        if valore is None:
            self.logger.warning(f"Bean con chiave '{chiave}' non trovato.")
        return valore

    def log_mappa_lunghezza(self):
        self.logger.info(f"Lunghezza della mappa dopo l'aggiunta: {(self._beans)}")

