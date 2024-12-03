import tkinter as tk
from tkinter import ttk

class VistaPrincipale(tk.Frame):
    def __init__(self, master=None, controllo_principale=None, modello=None):
        super().__init__(master)
        self.master = master
        self.controllo_principale = controllo_principale  # Passiamo il controllo principale
        self.modello = modello  # Passiamo il riferimento al modello
        self.create_widgets(master)

    def create_widgets(self, master):
        # Bottone per avviare la scansione
        self.label = tk.Label(master, text="Benvenuto nella Scansione!")
        self.label.pack(padx=10, pady=10)

        if self.controllo_principale:
            self.bottone = tk.Button(master, text="Avvia Scansione",
                                     command=self.controllo_principale.azione_avvia_scansione)
            self.bottone.pack(pady=10)  # Aggiunto padding per separare il bottone dalla tabella
        else:
            raise ValueError("controllo_principale non è stato inizializzato correttamente!")

        # Frame per Treeview e scrollbar
        frame_tree = ttk.Frame(master)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Aggiunge scrollbar verticali e orizzontali
        self.scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        self.scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # Treeview per visualizzare i dispositivi
        colonne = ["IP", "MAC", "Sistema Operativo", "TTL", "Tempo di Risposta", "Servizi Attivi", "Tipologia"]
        self.tree = ttk.Treeview(frame_tree, columns=colonne, show="headings",
                                 yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Associa le scrollbar al Treeview
        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)

        # Definiamo le colonne
        for col in colonne:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150, minwidth=100)  # Larghezza fissa, minwidth per scroll

        self.tree.pack(fill="both", expand=True)

        # Label per "Subnet Trovate" e "Numero Dispositivi Trovati"
        self.label_subnet = tk.Label(master, text="")
        self.label_subnet.pack(pady=5)

        self.label_dispositivi = tk.Label(master, text="")
        self.label_dispositivi.pack(pady=5)

    def aggiorna_stato(self, stato):
        """Aggiorna lo stato nella label."""
        self.label.config(text=stato)

    def aggiorna_risultato(self, dispositivo):
        """Aggiungi un dispositivo alla tabella."""
        # Popola la tabella con i dati del dispositivo
        self.tree.insert("", "end", values=(
            dispositivo['IP'], dispositivo['MAC'], dispositivo['Sistema Operativo'], dispositivo['TTL'],
            dispositivo['Tempo di Risposta'],
            ", ".join([f"{port}: {service}" for port, service in dispositivo['Servizi Attivi'].items()]),
            dispositivo['Tipologia']
        ))

    def carica_dispositivi(self):
        """Carica i dispositivi nella tabella."""
        # Ottieni i dispositivi dal modello
        lista_dispositivi = self.modello.ottieni_bean("DISPOSITIVI")

        # Pulisce la tabella prima di caricare i nuovi dispositivi
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Aggiungi ogni dispositivo alla tabella
        for dispositivo in lista_dispositivi:
            self.aggiorna_risultato(dispositivo)

    def aggiorna_info(self):
        # Aggiornamento dei valori nelle label dopo la scansione
        self.label_dispositivi.config(
            text=f"Numero Dispositivi Trovati: {len(self.modello.ottieni_bean('DISPOSITIVI'))}"
        )
