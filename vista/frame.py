from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction

class Frame(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inizializzazione dei componenti
        self.initComponents()

    def initComponents(self):
        """Metodo che inizializza i componenti della finestra"""
        self.setWindowTitle("Finestra Principale")
        self.setGeometry(100, 100, 648, 516)  # Posizione e dimensioni della finestra

        # Creazione della barra dei menu
        self.menubar = self.menuBar()

        # Creazione del menu "File"
        self.menu_file = self.menubar.addMenu("File")

        # Aggiunta dell'opzione "Esci"
        self.esci_action = QAction("Esci", self)
        self.esci_action.triggered.connect(self.esci)  # Connessione al metodo esci()
        self.menu_file.addAction(self.esci_action)

    def esci(self):
        """Metodo per chiudere l'applicazione"""
        self.close()
