import tkinter as tk
from tkinter import ttk

from modello.costanti import Costanti
from modello.scanner import ScannerRete
import threading
import logging

class ControlloPrincipale:
    def __init__(self, modello, vista_principale, logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(logging.StreamHandler())
        self.logger = logger
        self.scanner = ScannerRete(self.logger)
        self.vista_principale = vista_principale
        self.modello = modello

    def azione_avvia_scansione(self):
        # Crea la finestra di dialogo modale
        dialog = tk.Toplevel(self.vista_principale)
        dialog.title("Scansione in corso")
        dialog.geometry("300x100")
        dialog.transient(self.vista_principale)  # Fa sì che la finestra sia figlia della finestra principale
        dialog.grab_set()  # Rende la finestra modale

        # Centra la finestra di dialogo rispetto alla finestra principale
        self.centra_finestra(dialog, 300, 100)

        # Etichetta informativa
        label = ttk.Label(dialog, text="Scansione in corso...", font=("Arial", 12))
        label.pack(expand=True, pady=20)

        # Funzione per avviare la scansione in un thread separato
        def esegui_scansione():
            try:
                self.logger.debug("Avvio della scansione...")
                dispositivi = self.scanner.scan()
                self.modello.aggiungi_bean(Costanti.DISPOSITIVI, dispositivi)
                self.logger.debug(f"Dispositivi aggiunti: {dispositivi}")

                # Aggiorna la vista dopo la scansione
                if self.vista_principale:
                    self.vista_principale.carica_dispositivi()
                    self.vista_principale.aggiorna_info()
            finally:
                # Chiude la finestra di dialogo dopo la scansione
                dialog.destroy()

        # Avvia la scansione in un thread separato per non bloccare l'interfaccia grafica
        threading.Thread(target=esegui_scansione, daemon=True).start()

    def centra_finestra(self, finestra, larghezza, altezza):
        """Centra la finestra rispetto alla finestra principale."""
        finestra_principale = self.vista_principale.master  # Tk root
        finestra_principale.update_idletasks()  # Aggiorna le dimensioni

        # Calcola la posizione
        x_pos = finestra_principale.winfo_x() + (finestra_principale.winfo_width() // 2) - (larghezza // 2)
        y_pos = finestra_principale.winfo_y() + (finestra_principale.winfo_height() // 2) - (altezza // 2)

        # Imposta la geometria della finestra
        finestra.geometry(f"{larghezza}x{altezza}+{x_pos}+{y_pos}")
