# vista/vista_principale.py
import tkinter as tk

class VistaPrincipale(tk.Frame):
    def __init__(self, master=None, controllo_principale=None):
        super().__init__(master)
        self.master = master
        self.controllo_principale = controllo_principale  # Passiamo il controllo principale
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Benvenuto nella Scansione!")
        self.label.pack(padx=10, pady=10)  # Mostra la label

        self.bottone = tk.Button(self, text="Avvia Scansione", command=self.controllo_principale.azione_avvia_scansione)
        self.bottone.pack(padx=10, pady=10)  # Mostra il bottone
