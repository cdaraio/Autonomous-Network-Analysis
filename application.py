import logging
from PyQt5.QtWidgets import QApplication
from controllo.controlloFrame import ControlloFrame
from controllo.controlloVistaPrincipale import ControlloPrincipale
from modello.modello import Modello
from vista.frame import Frame  # Importa la tua classe Frame
from modello.scanner import ScannerRete # Importa la classe ScannerRete

# Configurazione del logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log in console
        logging.FileHandler("network_scan.log")  # Log in file
    ]
)

class Applicazione:
    _singleton = None

    def __new__(cls):
        """Gestisce la creazione dell'istanza Singleton."""
        if cls._singleton is None:
            cls._singleton = super(Applicazione, cls).__new__(cls)
        return cls._singleton

    def __init__(self):
        """Inizializza l'applicazione solo una volta."""
        if not hasattr(self, 'initialized'):  # Verifica se l'istanza è già stata inizializzata
            self.logger = logging.getLogger(__name__)  # Assicurati che il logger venga inizializzato
            self.controllo_frame = None
            self.controllo_principale = None
            self.modello = None
            self.frame = None  # Frame da aggiungere
            self.scanner_rete = ScannerRete(self.logger)  # Passa il logger direttamente alla classe ScannerRete
            self.initialized = True

    def inizializza(self):
        """Inizializzazione dei componenti dell'applicazione."""
        self.controllo_frame = ControlloFrame()
        self.controllo_principale = ControlloPrincipale()
        self.modello = Modello()

        # Inizializzazione del Frame
        self.frame = Frame()  # Supponiamo che tu abbia questa classe nella tua applicazione
        self.frame.initComponents()  # Assicurati che la funzione initComponents() venga chiamata per inizializzare gli elementi grafici
        #self.frame.show()  # Mostra il frame

        # Avvia la scansione della rete
        self.scanner_rete.scan()  # Esegui la scansione della rete

    @staticmethod
    def main():
        """Metodo main che avvia l'applicazione."""
        applicazione = Applicazione.get_instance()
        applicazione.inizializza()

    @staticmethod
    def get_instance():
        """Metodo per ottenere l'istanza singleton."""
        return Applicazione()

if __name__ == "__main__":
    app = QApplication([])  # Creiamo l'istanza di QApplication per avviare la GUI

    # Avvia l'applicazione
    applicazione = Applicazione.get_instance()
    applicazione.inizializza()

    app.exec_()  # Avvia l'evento loop di Qta
