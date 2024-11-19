# applicazione/application.py
import tkinter as tk
import logging
from vista.vista_principale import VistaPrincipale
from controllo.controlloPrincipale import ControlloPrincipale


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
        self.logger = logging.getLogger(__name__)
        self.frame = None
        self.vista_principale = None
        self.controllo_principale = None

    def inizializza(self):
        """Inizializzazione dei componenti dell'applicazione."""
        self.frame = tk.Tk()  # Crea la finestra principale
        self.frame.title("Network Topology Mapper")

        # Imposta la dimensione della finestra
        window_width = 400
        window_height = 300

        # Ottieni le dimensioni dello schermo
        screen_width = self.frame.winfo_screenwidth()
        screen_height = self.frame.winfo_screenheight()

        # Calcola la posizione per centrare la finestra
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Imposta la geometria della finestra
        self.frame.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Porta la finestra in primo piano forzatamente
        self.frame.attributes("-topmost", True)  # Questo la mette sempre in primo piano
        self.frame.lift()  # Altra opzione per cercare di alzarla
        self.frame.after(100, lambda: self.frame.attributes("-topmost", False))  # Imposta a False dopo 100ms

        # Crea l'istanza di ControlloPrincipale, passando la vista
        self.controllo_principale = ControlloPrincipale(None, self.logger)

        # Crea la vista principale, passando il controllo
        self.vista_principale = VistaPrincipale(self.frame, self.controllo_principale)
        self.vista_principale.pack()  # Aggiungi la vista al contenitore principale

        self.frame.mainloop()  # Avvia il loop dell'interfaccia grafica

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
