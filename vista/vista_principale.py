import tkinter as tk
from tkinter import ttk, messagebox


class VistaPrincipale(tk.Frame):
    def __init__(self, master=None, controllo_principale=None, modello=None):
        super().__init__(master)
        self.master = master
        self.controllo_principale = controllo_principale
        self.modello = modello
        self.widgets = []
        self.colonne_result = ["Hop", "Indirizzo IP", "Tempo di Risposta(ms)", "Hostname", "Regione"]
        self.create_widgets(master)
        self.mostra_componenti_traceroute()
        self.dialog = None

    def create_widgets(self, master):
        titolo_label = tk.Label(master, text="Scansione Rete", font=("Tahoma", 16))
        scansione_frame = tk.Frame(self.master)
        scansione_frame.pack(pady=10)  # Spaziatura uniforme attorno al frame
        scansione_frame.widget_name = "scansione_frame"
        self.widgets.append(scansione_frame)

        # Bottone per avviare la scansione
        if self.controllo_principale:
            self.bottone_scansione = tk.Button(
                scansione_frame, text="Avvia Scansione",
                command=self.controllo_principale.azione_avvia_scansione
            )
            self.bottone_scansione.pack(side="left", padx=5)  # Margine laterale tra i bottoni
            self.bottone_scansione.widget_name = "bottone_scansione"
            self.widgets.append(self.bottone_scansione)
        else:
            raise ValueError("controllo_principale non è stato inizializzato correttamente!")

        # Bottone per visualizzare il grafo
        self.bottone_grafo = tk.Button(
            scansione_frame, text="Visualizza Grafo",
            command=self.controllo_principale.visualizza_grafo
        )
        self.bottone_grafo.pack(side="left", padx=5)  # Margine laterale tra i bottoni
        self.bottone_grafo.widget_name = "bottone_grafo"
        self.widgets.append(self.bottone_grafo)

        # Frame per Treeview e scrollbar
        tabella = ttk.Frame(master)
        tabella.pack(fill="both", expand=True, padx=10, pady=10)
        tabella.widget_name = "tabella"
        self.widgets.append(tabella)
        # Scrollbar
        self.scrollbar_y_scansione = ttk.Scrollbar(tabella, orient="vertical")
        self.scrollbar_y_scansione.widget_name = "scrollbar_y_scansione"
        self.widgets.append(self.scrollbar_y_scansione)
        self.scrollbar_y_scansione.pack(side="right", fill="y")

        self.scrollbar_x_scansione = ttk.Scrollbar(tabella, orient="horizontal")
        self.scrollbar_x_scansione.widget_name = "scrollbar_y_scansione"
        self.widgets.append(self.scrollbar_x_scansione)
        self.scrollbar_x_scansione.pack(side="bottom", fill="x")

        # Treeview per visualizzare i dispositivi
        colonne = ["IP", "MAC", "Sistema Operativo", "TTL", "Tempo di Risposta", "Servizi Attivi", "Tipologia"]
        self.tree = ttk.Treeview(tabella, columns=colonne, show="headings",
                                 yscrollcommand=self.scrollbar_y_scansione.set, xscrollcommand=self.scrollbar_x_scansione.set)

        # Associa le scrollbar al Treeview
        self.scrollbar_y_scansione.config(command=self.tree.yview)
        self.scrollbar_x_scansione.config(command=self.tree.xview)

        # Definizione colonne
        for col in colonne:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150, minwidth=100)  # Larghezza fissa, minwidth per scroll
        self.tree.pack(fill="both", expand=True)

        # Label per "Numero Dispositivi Trovati"

        self.label_dispositivi = tk.Label(master, text="")
        self.widgets.append(self.label_dispositivi)
        self.label_dispositivi.pack(side="top", padx=3)

    def aggiorna_risultato(self, dispositivo):
        # Popola la tabella con i dati del dispositivo
        self.tree.insert("", "end", values=(
            dispositivo['IP'], dispositivo['MAC'], dispositivo['Sistema Operativo'], dispositivo['TTL'],
            dispositivo['Tempo di Risposta'],
            ", ".join([f"{port}: {service}" for port, service in dispositivo['Servizi Attivi'].items()]),
            dispositivo['Tipologia']
        ))

    def carica_dispositivi(self):
        """Carica i dispositivi nella tabella."""
        lista_dispositivi = self.modello.ottieni_bean("DISPOSITIVI")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for dispositivo in lista_dispositivi:
            self.aggiorna_risultato(dispositivo)

    def aggiorna_info(self):
        self.label_dispositivi.config(
            text=f"Numero Dispositivi Trovati: {len(self.modello.ottieni_bean('DISPOSITIVI'))}"
        )

    def mostra_componenti_traceroute(self):
        titolo_label = tk.Label(self.master, text="Traceroute", font=("Tahoma", 16))
        titolo_label.pack(pady=2)
        # Frame per input traceroute
        traceroute_frame = tk.Frame(self.master)
        traceroute_frame.pack(pady=2, fill="x")  # Ridotto il padding superiore
        traceroute_frame.widget_name = "traceroute_frame"
        self.widgets.append(traceroute_frame)

        # Etichetta "Indirizzo"
        self.label_traceroute = tk.Label(traceroute_frame, text="Indirizzo:")
        self.label_traceroute.pack(side="left", padx=5)
        self.label_traceroute.widget_name = "label_traceroute"
        self.widgets.append(self.label_traceroute)

        # Campo di input
        self.entry_traceroute = tk.Entry(traceroute_frame, width=30)
        self.entry_traceroute.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_traceroute.widget_name = "entry_traceroute"
        self.widgets.append(self.entry_traceroute)

        # Bottone "Avvia"
        self.bottone_esegui_traceroute = tk.Button(
            traceroute_frame, text="Avvia",
            command=lambda: self.controllo_principale.avvia_traceroute(self.entry_traceroute.get())
        )
        self.bottone_esegui_traceroute.pack(side="left", padx=5)
        self.bottone_esegui_traceroute.widget_name = "bottone_esegui_traceroute"
        self.widgets.append(self.bottone_esegui_traceroute)
        self.entry_traceroute.bind("<Return>", lambda event: self.controllo_principale.avvia_traceroute(
            self.entry_traceroute.get()))

        # Frame per risultati
        frame_result = ttk.Frame(self.master)
        frame_result.pack(fill="both", expand=True, padx=10, pady=5)
        frame_result.widget_name = "frame_result"
        self.widgets.append(frame_result)

        # Scrollbar verticale
        self.scrollbar_y_result = ttk.Scrollbar(frame_result, orient="vertical")
        self.scrollbar_y_result.pack(side="right", fill="y")
        self.scrollbar_y_result.widget_name = "scrollbar_y_result"
        self.widgets.append(self.scrollbar_y_result)

        # Scrollbar orizzontale
        self.scrollbar_x_result = ttk.Scrollbar(frame_result, orient="horizontal")
        self.scrollbar_x_result.pack(side="bottom", fill="x")
        self.scrollbar_x_result.widget_name = "scrollbar_x_result"
        self.widgets.append(self.scrollbar_x_result)

        # Tabella dei risultati
        self.tree_result = ttk.Treeview(
            frame_result, columns=self.colonne_result, show="headings",
            yscrollcommand=self.scrollbar_y_result.set,
            xscrollcommand=self.scrollbar_x_result.set
        )

        self.scrollbar_y_result.config(command=self.tree_result.yview)
        self.scrollbar_x_result.config(command=self.tree_result.xview)

        for col in self.colonne_result:
            self.tree_result.heading(col, text=col)
            self.tree_result.column(col, anchor="center", width=150, minwidth=100)

        self.tree_result.pack(fill="both", expand=True)
        self.tree_result.widget_name = "tree_result"
        self.widgets.append(self.tree_result)

    def aggiorna_tabella_risultati(self):
        lista_traceroute = self.modello.ottieni_bean("Traceroute")
        if lista_traceroute and len(lista_traceroute) > 0:
            for item in self.tree_result.get_children():
                self.tree_result.delete(item)

            for risultato in lista_traceroute:
                tempo_ms_format = f"{risultato.tempo_ms:.3f}"
                self.tree_result.insert(
                    "", "end",
                    values=(risultato.hop, risultato.ip, tempo_ms_format, risultato.hostname, risultato.regione)
                )
        else:
            messagebox.showerror("Errore", "Nessun risultato trovato per il traceroute.")

    def mostra_messaggio_errore(self, title, message):
        messagebox.showerror(title, message)
        return

    def centra_finestra(self, finestra, larghezza, altezza):
        finestra_principale = self.master
        finestra_principale.update_idletasks()
        x_pos = finestra_principale.winfo_x() + (finestra_principale.winfo_width() // 2) - (larghezza // 2)
        y_pos = finestra_principale.winfo_y() + (finestra_principale.winfo_height() // 2) - (altezza // 2)
        finestra.geometry(f"{larghezza}x{altezza}+{x_pos}+{y_pos}")
