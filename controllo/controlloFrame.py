from tkinter import messagebox
from modello.costanti import Costanti

class ControlloFrame:
    def __init__(self):
        self.nome_app = Costanti.NOME_APP
        self.versione = Costanti.VERSIONE
        self.autori = Costanti.AUTORI
        self.descrizione = Costanti.DESCRIZIONE_APP

    def mostra_guida(self):
        guida = Costanti.GUIDA
        messagebox.showinfo("Guida", guida)

    def mostra_informazioni(self):
        informazioni = (
            f"{self.nome_app}\n"
            f"Versione: {self.versione}\n\n"
            "Autori:\n" + "\n".join(self.autori) + "\n\n"
            f"Descrizione:\n{self.descrizione}\n\n"
            "Grazie per aver scelto la nostra applicazione!"
        )
        messagebox.showinfo("Informazioni su", informazioni)
