from typing import Any, Dict
import logging

class Modello:
    def __init__(self):
        self._beans: Dict[str, Any] = {}
        # Configura il logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def aggiungi_bean(self, chiave: str, valore: Any):
        """Aggiungi un bean al dizionario e logga la lunghezza della mappa e del valore (se è una lista)."""
        self._beans[chiave] = valore
        self.log_mappa_lunghezza()  # Logga la lunghezza della mappa

        if isinstance(valore, list):
            # Se il valore è una lista (come nel caso dei dispositivi), logga la sua lunghezza
            self.logger.info(f"Lunghezza della lista di dispositivi: {len(valore)}")

    def ottieni_bean(self, chiave: str) -> Any:
        """Ottieni un bean dal dizionario."""
        valore = self._beans.get(chiave)
        if valore is None:
            self.logger.warning(f"Bean con chiave '{chiave}' non trovato.")
        return valore

    def log_mappa_lunghezza(self):
        """Logga la lunghezza del dizionario _beans."""
        self.logger.info(f"Lunghezza della mappa dopo l'aggiunta: {len(self._beans)}")
