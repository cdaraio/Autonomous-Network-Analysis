import tkinter as tk
import threading

class VistaPrincipale(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Benvenuto nella Scansione!")
        self.label.pack(padx=10, pady=10)  # Mostra la label

        self.bottone = tk.Button(self, text="Avvia Scansione", command=self.avvia_scansione)
        self.bottone.pack(padx=10, pady=10)  # Mostra il bottone

    def avvia_scansione(self):
        self.label.config(text="Scansione Iniziata...")
        threading.Thread(target=self.scansione_rilevamento).start()

    def scansione_rilevamento(self):
        # Simula un processo di scansione lento
        import time
        time.sleep(5)  # Simula un'attività che richiede tempo
        self.label.config(text="Scansione Completa!")

def run_app():
    root = tk.Tk()  # Crea la finestra principale
    root.title("Network Topology Mapper")
    app = VistaPrincipale(master=root)  # Crea l'istanza della vista
    app.pack()  # Aggiungi la vista al contenitore principale
    root.mainloop()  # Avvia il loop dell'interfaccia grafica

if __name__ == "__main__":
    run_app()
