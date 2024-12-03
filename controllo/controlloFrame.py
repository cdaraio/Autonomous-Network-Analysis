from tkinter import messagebox

from modello.costanti import Costanti


class ControlloFrame:
    def __init__(self):
        self.nome_app = Costanti.NOME_APP
        self.versione = Costanti.VERSIONE
        self.autori = Costanti.AUTORI
        self.descrizione = Costanti.DESCRIZIONE_APP

    def mostra_guida(self):
        guida = (
              "Benvenuto nella guida di " + Costanti.NOME_APP + "!\n\n"
        "Grazie per aver scelto " + Costanti.NOME_APP + ",l’app per scansionare e mappare facilmente la tua rete.\n"
        "Ecco come iniziare:\n\n"
        "1. Avviare una scansione:\n"
        "   Dalla schermata principale, premi il pulsante 'Avvia Scansione' per iniziare l’analisi della rete.\n\n"
        "2. Visualizzare i risultati:\n"
        "   Una volta completata la scansione, i risultati verranno mostrati nella finestra principale dell’app.\n\n"
        "3. Accedere alla guida:\n"
        "   Usa il menu 'Aiuto' per consultare ulteriori istruzioni o ottenere informazioni sull’applicazione.\n\n"
        "Per maggiori dettagli, visita la documentazione ufficiale o contatta il nostro supporto tecnico.\n\n"
        )
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
