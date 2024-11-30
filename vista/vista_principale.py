import tkinter as tk
from tkinter import ttk

class VistaPrincipale(tk.Frame):
    def __init__(self, master=None, controllo_principale=None, modello=None):
        super().__init__(master)
        self.master = master
        self.controllo_principale = controllo_principale  # Passiamo il controllo principale
        self.modello = modello  # Passiamo il riferimento al modello
        self.create_widgets()

    def create_widgets(self):
        # Bottone per avviare la scansione
        self.label = tk.Label(self, text="Benvenuto nella Scansione!")
        self.label.pack(padx=10, pady=10)
        if self.controllo_principale:
            self.bottone = tk.Button(self, text="Avvia Scansione",
                                     command=self.controllo_principale.azione_avvia_scansione)
            self.bottone.pack(pady=10)  # Aggiunto padding per separare il bottone dalla tabella
        else:
            raise ValueError("controllo_principale non è stato inizializzato correttamente!")

        # Frame per contenere Treeview e Scrollbar
        frame_tabella = tk.Frame(self)
        frame_tabella.pack(fill="both", expand=True, padx=10, pady=10)  # Occupa tutto lo spazio disponibile

        # Treeview per visualizzare i dispositivi
        self.tree = ttk.Treeview(frame_tabella, columns=(
            "IP", "MAC", "Sistema Operativo", "TTL", "Tempo di Risposta", "Servizi Attivi", "Tipologia"), show="headings")

        # Definiamo le colonne
        colonne = ["IP", "MAC", "Sistema Operativo", "TTL", "Tempo di Risposta", "Servizi Attivi", "Tipologia"]
        for col in colonne:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150, stretch=True)  # Stretch rende le colonne adattive

        # Scrollbar verticale
        scrollbar_y = ttk.Scrollbar(frame_tabella, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        # Scrollbar orizzontale
        scrollbar_x = ttk.Scrollbar(frame_tabella, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        # Posizionamento con grid()
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Configurazione della griglia per espandere il frame
        frame_tabella.rowconfigure(0, weight=1)
        frame_tabella.columnconfigure(0, weight=1)

        # Assicurarsi che il frame principale si espanda
        self.pack(fill="both", expand=True)

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
