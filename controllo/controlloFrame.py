class ControlloFrame:
    def __init__(self):
       self._modello = None  # Esempio di riferimento al modello (da inizializzare successivamente)

    def inizializza(self, modello):
        """Inizializza il controller con un riferimento al modello."""
        self._modello = modello
        print("ControlloPrincipale: inizializzazione completata.")

    def esegui_azione(self, azione):
        """Metodo per eseguire una certa azione. Può essere esteso per azioni specifiche."""
        print(f"Eseguendo azione: {azione}")
        # Aggiungere la logica per l'azione
        # Ad esempio, il controller può modificare il modello o aggiornare la vista

    def aggiorna_vista(self):
        """Metodo per aggiornare la vista o il modello in base alle modifiche."""
        if self._modello:
            # Logica per aggiornare la vista tramite il modello
            print("Aggiornamento della vista in base ai cambiamenti nel modello.")
        else:
            print("Errore: modello non inizializzato.")

    def gestisci_evento(self, evento):
        """Gestisce un evento specifico dall'interfaccia utente o da un altro componente."""
        print(f"Gestendo evento: {evento}")
        # Logica di gestione evento (ad esempio, risposta a un clic del pulsante)
        self.esegui_azione(evento)
