# controllo/controllo_principale.py
from modello.scanner import ScannerRete


class ControlloPrincipale:
    def __init__(self, vista_principale=None, logger=None):
        self.vista_principale = vista_principale
        self.logger = logger
        self.scanner = ScannerRete(logger)  # Inizializza ScannerRete

    def azione_avvia_scansione(self):
        # Logica di avvio della scansione
        self.logger.debug("Avvio della scansione...")

        # Avvia la scansione chiamando il metodo di ScannerRete
        self.scanner.scan()
