import tkinter as tk
import logging

from modello.modello import Modello
from vista.vista_principale import VistaPrincipale
from vista.frame import MainFrame

# Logger configurazione
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log in console
        logging.FileHandler("network_scan.log")  # Log in file
    ]
)

class Application:
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
            cls._singleton._init_singleton(*args, **kwargs)
        return cls._singleton

    def _init_singleton(self):
        """Inizializza una sola volta."""
        self.logger = logging.getLogger(__name__)  # Logger inizializzato qui
        self.vista_principale = None
        self.controllo_principale = None
        self.modello = Modello()

    def inizializza(self):
        from controllo.controlloPrincipale import ControlloPrincipale
        """Inizializzazione dei componenti dell'applicazione."""

        # Crea la finestra principale
        self.frame = MainFrame()
        # Crea il ControlloPrincipale senza la vista
        self.controllo_principale = ControlloPrincipale(self.modello, vista_principale=None, logger=self.logger)

        # Crea la VistaPrincipale e passa il ControlloPrincipale
        self.vista_principale = VistaPrincipale(self.frame, controllo_principale=self.controllo_principale,
                                                modello=self.modello)
        # Aggiornamento del ControlloPrincipale con la vista
        self.controllo_principale.vista_principale = self.vista_principale
        self.frame.set_view(self.vista_principale)  # Imposta la vista principale
        self.frame.mainloop()

    @staticmethod
    def main():
        """Metodo main che avvia l'applicazione."""
        applicazione = Application.get_instance()
        applicazione.inizializza()

    @staticmethod
    def get_instance():
        """Metodo per ottenere l'istanza singleton."""
        return Application()


# Avvio dell'applicazione
if __name__ == "__main__":
    applicazione = Application.get_instance()
    applicazione.main()  # Avvia l'applicazione
