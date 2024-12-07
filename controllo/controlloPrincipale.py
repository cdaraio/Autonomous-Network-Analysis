import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

import webview
from pyvis.network import Network
from tkinterhtml import HtmlFrame
from modello.costanti import Costanti
from modello.dispositivo import Dispositivo
from modello.enum_dispositivo import TipoDispositivo
from modello.scanner import ScannerRete
import threading
import logging
import os

from vista.vista_grafo import ExtraGraphWindow


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

    # Funzione per visualizzare il grafo in una nuova finestra
    def visualizza_grafo2(self):
        dispositivi = self.modello.ottieni_bean(Costanti.DISPOSITIVI)
        path_grafo = self.crea_grafo(dispositivi)

        # Crea una nuova finestra per visualizzare il grafo
        new_window = tk.Toplevel()
        new_window.title("Grafo Interattivo")

        html_frame = HtmlFrame(new_window, width=800, height=600)
        html_frame.pack(fill="both", expand=True)

        # Mostra il contenuto HTML nel frame
        with open(path_grafo, 'r') as file:
            html_content = file.read()
        html_frame.set_content(html_content)

    def visualizza_grafo(self):
        dispositivi = self.modello.ottieni_bean("DISPOSITIVI")
        if dispositivi is None:
            messagebox.showerror(title="Visualizza Grafo", message="Nessun dispositivo rilevato dalla scansione")
            return

        path_grafo = self.crea_grafo(dispositivi)
        ExtraGraphWindow(self.vista_principale, path_grafo)  # Apri una finestra secondaria

    def crea_grafo(self, dispositivi):
        net = Network(notebook=False, height="800px", width="100%", bgcolor="#222222", font_color="white")

        # Configura la simulazione fisica
        net.barnes_hut(
            gravity=-30000,  # Forza gravitazionale per distanziare i nodi
            central_gravity=0.3,  # Gravità centrale per tenere i nodi vicini
            spring_length=200,  # Lunghezza preferita degli archi
            spring_strength=0.02  # Forza elastica tra i nodi
        )
        router = None
        for dispositivo in dispositivi:
            if dispositivo["Tipologia"] == 'Router':
                print("Router collegato al centro")
                router = dispositivo
                break

        if router:
            # Se il router viene trovato, aggiungilo come nodo centrale
            net.add_node(router["IP"], label=f"Router\nIP: {router['IP']}\nMAC: {router['MAC']}", color="red", size=30,
                         icon="fa fa-cogs")

            # Aggiungi gli altri dispositivi come nodi e collegali al router
            for dispositivo in dispositivi:
                if dispositivo != router:  # Escludi il router
                    net.add_node(dispositivo["IP"],
                                 label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                                 color="lightblue", size=20, icon="fa fa-desktop")
                    net.add_edge(router["IP"], dispositivo["IP"])  # Collegamento al router

        else:
            # Se il router non è stato trovato, aggiungi i nodi e collega tutti i dispositivi tra loro
            for dispositivo in dispositivi:
                net.add_node(dispositivo["IP"],
                             label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                             color="lightgreen", size=20, icon="fa fa-desktop")

            # Collega tutti i dispositivi tra loro
            for i in range(len(dispositivi)):
                for j in range(i + 1, len(dispositivi)):
                    net.add_edge(dispositivi[i]["IP"], dispositivi[j]["IP"])

        # Salva il grafo come file HTML
        output_path = os.path.abspath("grafo_interattivo.html")
        net.save_graph(output_path)

        return output_path

    # Funzione per creare il grafo
    def crea_grafo2(self, dispositivi):
        net = Network(notebook=False, height="800px", width="100%", bgcolor="#222222", font_color="white")

        # Configura la simulazione fisica
        net.barnes_hut(
            gravity=-30000,  # Forza gravitazionale per distanziare i nodi
            central_gravity=0.3,  # Gravità centrale per tenere i nodi vicini
            spring_length=200,  # Lunghezza preferita degli archi
            spring_strength=0.05  # Forza elastica tra i nodi
        )
        # Aggiungi nodi e collegamenti al grafo
        for dispositivo in dispositivi:
            net.add_node(dispositivo["IP"], label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}")

        for i in range(len(dispositivi)):
            for j in range(i + 1, len(dispositivi)):
                net.add_edge(dispositivi[i]["IP"], dispositivi[j]["IP"])

        # Salva il grafo come file HTML
        output_path = os.path.abspath("grafo_interattivo.html")
        net.save_graph(output_path)

        return output_path

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
                if len(dispositivi) == 0:
                    dialog.destroy()
                    informazioni = (
                        "Nessun dispositivo trovato sulla rete"
                    )
                    messagebox.showinfo("Risultato Scansione", informazioni)
                else:
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
