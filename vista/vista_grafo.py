import tkinter as tk
import webview

class ExtraGraphWindow(tk.Toplevel):
    def __init__(self, master, path_grafo):
        super().__init__(master)
        self.title('Grafo Interattivo')
        self.geometry('800x600')

        # Salva il percorso del grafo e crea la finestra WebView
        self.path_grafo = path_grafo
        self.webview_window = None

        # Disabilita il tasto di chiusura (X)
        self.protocol("WM_DELETE_WINDOW", self.on_close_blocked)

        # Mostra il grafo interattivo
        self.show_graph()


    def show_graph(self):
        """Avvia WebView in modalità non bloccante"""
        self.webview_window = webview.create_window("Grafo Interattivo", self.path_grafo)
        webview.start(gui='qt', debug=True)

    def on_close_blocked(self):
        print("Tentativo di chiusura tramite il tasto X ignorato.")

    def on_close(self):
        if self.webview_window is not None:
            try:
                print("Finestra WebView in chiusura...")
                self.webview_window.destroy()
                self.webview_window = None
            except Exception as e:
                print(f"Errore durante la chiusura della finestra WebView: {e}")

        self.destroy()
