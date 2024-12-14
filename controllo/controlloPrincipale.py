import socket
import subprocess
import tkinter as tk
from datetime import time
from tkinter import ttk, messagebox
import socket
import struct
import time

import ipinfo
from scapy.all import *
import argparse
from pyvis.network import Network
from scapy.layers.inet import traceroute, UDP, IP
from tkinterhtml import HtmlFrame
from modello.costanti import Costanti
from modello.enum_dispositivo import TipoDispositivo
from modello.scanner import ScannerRete
import threading
import logging
import os

from modello.traceroute import Traceroute
from vista.vista_grafo import ExtraGraphWindow


class ControlloPrincipale:
    def __init__(self, modello, vista_principale, logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(logging.StreamHandler())
        self.logger = logger
        self.scanner = ScannerRete(self.logger)
        self.vista_principale = vista_principale
        self.lista_traceroute = []
        self.scansione_interrotta = False
        self.thread_scansione = None
        self.modello = modello
        # Inizializzazione ipinfo_handler
        access_token = "4614054d77f209"  #token API
        self.ipinfo_handler = ipinfo.getHandler(access_token)

    def avvia_traceroute(self, target):
        """Avvia la scansione e aggiorna la tabella dopo il completamento del thread."""

        def esegui_traceroute():
            """Funzione per eseguire il traceroute in un thread separato."""
            try:
                # Verifica che il target non sia vuoto prima di mostrare la finestra di dialogo
                if not target:
                    # Se il target è vuoto, mostra solo l'errore senza procedere ulteriormente
                    self.vista_principale.mostra_messaggio_errore("Errore", "Il campo indirizzo non può essere vuoto.")
                    return

                # Crea una finestra di dialogo per il progresso
                self.dialogo = tk.Toplevel(self.vista_principale)
                self.dialogo.title("Traceroute in corso")
                self.dialogo.grab_set()
                # Disabilita la "X" di chiusura
                self.dialogo.protocol("WM_DELETE_WINDOW", self.ignora_chiusura)

                # Etichetta per il messaggio
                etichetta = ttk.Label(self.dialogo, text=f"Traceroute verso {target} in corso...")
                etichetta.pack(pady=10)

                # Progress bar in modalità determinata (con intervallo da 0 a 100)
                self.progress = ttk.Progressbar(self.dialogo, orient='horizontal', mode='determinate', length=250)
                self.progress.pack(pady=10, padx=20, fill='x')
                self.progress["value"] = 0  # Inizializza la progress bar a 0
                self.progress["maximum"] = 100  # Imposta il valore massimo a 100

                # Centra la finestra di dialogo con la progress bar
                self.centra_progress(self.dialogo, 300, 100)

                # Esegui il traceroute
                self.scan_traceroute(target, self.progress)

                # Una volta completata la scansione, chiudi la finestra di dialogo
                self.dialogo.destroy()

                # Una volta che i dati sono stati aggiornati nel modello, aggiorna la tabella dei risultati
                self.vista_principale.aggiorna_tabella_risultati()

            except Exception as e:
                # Gestisci le eccezioni: chiudi la finestra di dialogo e mostra il messaggio di errore
                if self.dialogo:
                    self.dialogo.destroy()  # Chiude la finestra di dialogo se c'è un errore
                self.vista_principale.mostra_messaggio_errore("Errore", f"Si è verificato un errore: {e}")

        # Crea un thread per eseguire la scansione senza bloccare la GUI
        thread = threading.Thread(target=esegui_traceroute)
        thread.start()  # Avvia il thread

    def ignora_chiusura(self):
        """Non fare nulla quando l'utente prova a chiudere la finestra"""
        pass

    def scan_traceroute(self, target, progress_bar):
        if not target:
            self.vista_principale.mostra_messaggio_errore("Errore", "Il campo indirizzo non può essere vuoto.")
            return

        # Verifica se il target è risolvibile tramite DNS
        try:
            socket.gethostbyname(target)
        except socket.gaierror:
            self.vista_principale.mostra_messaggio_errore("Errore di Connessione",
                                                          "Indirizzo non valido o non trovato.")
            return

        maxTTL = 24  # Numero massimo di hop
        targetIP = target

        self.lista_traceroute = []

        try:
            ttl = 1
            while ttl <= maxTTL:
                ip_packet = IP(dst=targetIP, ttl=ttl)
                udp_packet = UDP(dport=33434)
                packet = ip_packet / udp_packet

                # Invia il pacchetto e ricevi la risposta
                reply = sr1(packet, timeout=5, verbose=0)  # Aumentato timeout

                # Calcola e aggiorna la progress bar
                progresso = (ttl / maxTTL) * 100
                progress_bar["value"] = progresso
                self.dialogo.update_idletasks()  # Aggiorna la GUI

                if reply is None:
                    # Nessuna risposta, continua con il prossimo TTL
                    print("* * *")
                    ttl += 1
                    continue
                elif reply.type == 3:
                    # Destinazione raggiunta
                    print(f"{reply.src}")
                    ip = reply.src
                    tempo_ms = (reply.time - packet.sent_time) * 1000

                    hostname = self._get_hostname(ip) if ip else "N/D"
                    regione = self._get_regione(ip) if ip else "N/D"

                    risultato = Traceroute(ttl, ip, hostname, tempo_ms, regione)
                    self.lista_traceroute.append(risultato)

                    if ip == targetIP:
                        break
                else:
                    # Risposta intermedia
                    print(f"{reply.src}")
                    ip = reply.src
                    tempo_ms = (reply.time - packet.sent_time) * 1000

                    hostname = self._get_hostname(ip) if ip else "N/D"
                    regione = self._get_regione(ip) if ip else "N/D"

                    risultato = Traceroute(ttl, ip, hostname, tempo_ms, regione)
                    self.lista_traceroute.append(risultato)

                ttl += 1
                time.sleep(1)  # Aggiunto ritardo di 1 secondo tra i pacchetti

            if not self.lista_traceroute:
                self.vista_principale.mostra_messaggio_errore("Errore", "Nessun risultato trovato per il traceroute.")
                return

            self.modello.aggiungi_bean("Traceroute", self.lista_traceroute)

        except socket.gaierror as e:
            self.vista_principale.mostra_messaggio_errore("Errore di Connessione",
                                                          "Indirizzo non valido o non trovato.")
            print(f"Errore di connessione: {e}")
            return

        except Exception as e:
            self.vista_principale.mostra_messaggio_errore("Errore durante il traceroute",
                                                          f"Si è verificato un errore: {e}")
            return

    def _get_hostname(self, ip):
        try:
            from socket import gethostbyaddr
            return gethostbyaddr(ip)[0]
        except:
            return "N/D"

    def _get_regione(self, ip):
        """Restituisce la regione geografica per un dato IP utilizzando ipinfo_handler."""
        import ipaddress

        # Verifica se l'IP è valido
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print(f"IP non valido: {ip}")
            return "N/D"

        # Recupera i dettagli dal servizio ipinfo
        try:
            details = self.ipinfo_handler.getDetails(ip)

            # Accedi direttamente alla proprietà 'region' dell'oggetto Details
            regione = details.region if details.region else "Sconosciuta"  # Usa 'Sconosciuta' se la regione non è disponibile

            return regione

        except ConnectionError:
            print(f"Errore di connessione durante la risoluzione della regione per IP {ip}")
            return "N/D"
        except KeyError:
            print(f"Chiave 'region' mancante nei dettagli per IP {ip}")
            return "Sconosciuta"
        except Exception as e:
            print(f"Errore imprevisto per IP {ip}: {e}")
            return "N/D"

    def visualizza_grafo(self):
        dispositivi = self.modello.ottieni_bean("DISPOSITIVI")
        if dispositivi is None:
            self.vista_principale.mostra_messaggio_errore(title="Visualizza Grafo", message="Nessun dispositivo rilevato dalla scansione")
            return

        path_grafo = self.crea_grafo(dispositivi)
        ExtraGraphWindow(self.vista_principale, path_grafo)  # Apri una finestra secondaria

    def crea_grafo(self, dispositivi):
        net = Network(notebook=False, height="800px", width="100%", bgcolor="#222222", font_color="white")

        # Configura la simulazione fisica
        net.barnes_hut(
            gravity=-30000,  # Forza gravitazionale per distanziare i nodi
            central_gravity=0.3,  # Gravità centrale per tenere i nodi vicini
            spring_length=200,  # Lunghezza preferita degli archi
            spring_strength=0.02  # Forza elastica tra i nodi
        )

        # Dizionario per le icone associate alle tipologie
        icon_dict = {
            'Router': "src/images/router.png",  # Percorso per l'icona del router
            'Switch': "src/images/switch.png",  # Percorso per l'icona dello switch
            'Client': "src/images/client.png",  # Percorso per l'icona del client
            'Server': "src/images/server.png"  # Percorso per l'icona del server
        }

        router = None
        for dispositivo in dispositivi:
            if dispositivo["Tipologia"] == 'Router':
                print("Router collegato al centro")
                router = dispositivo
                break

        if router:
            # Se il router viene trovato, aggiungilo come nodo centrale
            net.add_node(router["IP"], label=f"Router\nIP: {router['IP']}\nMAC: {router['MAC']}", color="red", size=30,
                         image=icon_dict['Router'], shape="image")  # Usa l'immagine per il router

            # Aggiungi gli altri dispositivi come nodi e collegali al router
            for dispositivo in dispositivi:
                if dispositivo != router:  # Escludi il router
                    net.add_node(
                        dispositivo["IP"],
                        label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                        color="lightblue", size=20, image=icon_dict[dispositivo["Tipologia"]], shape="image"
                        # Usa l'immagine basata sulla tipologia
                    )
                    net.add_edge(router["IP"], dispositivo["IP"])  # Collegamento al router

        else:
            # Se il router non è stato trovato, aggiungi i nodi e collega tutti i dispositivi tra loro
            for dispositivo in dispositivi:
                net.add_node(
                    dispositivo["IP"],
                    label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                    color="lightgreen", size=20, image=icon_dict[dispositivo["Tipologia"]], shape="image"
                    # Usa l'immagine basata sulla tipologia
                )

            # Collega tutti i dispositivi tra loro
            for i in range(len(dispositivi)):
                for j in range(i + 1, len(dispositivi)):
                    net.add_edge(dispositivi[i]["IP"], dispositivi[j]["IP"])

        # Salva il grafo come file HTML
        output_path = os.path.abspath("grafo_interattivo.html")
        net.save_graph(output_path)

        return output_path

    def azione_avvia_scansione(self):
        # Crea la finestra di dialogo con una progress bar
        titolo = "Scansione in corso"
        self.dialogo = tk.Toplevel(self.vista_principale)
        self.dialogo.title(titolo)

        # Disabilita la "X" di chiusura
        self.dialogo.protocol("WM_DELETE_WINDOW", self.ignora_chiusura)

        # Etichetta per il messaggio
        etichetta = ttk.Label(self.dialogo, text="Scansione in corso...")
        etichetta.pack(pady=10)

        # Progress bar in modalità determinata (con intervallo da 0 a 100)
        self.progress = ttk.Progressbar(self.dialogo, orient='horizontal', mode='determinate', length=250)
        self.progress.pack(pady=10, padx=20, fill='x')
        self.progress["value"] = 0  # Inizializza la progress bar a 0
        self.progress["maximum"] = 100  # Imposta il valore massimo a 100

        # Centra la finestra di dialogo con la progress bar
        self.centra_progress(self.dialogo, 300, 100)

        # Funzione per avviare la scansione in un thread separato
        def esegui_scansione():
            try:
                self.logger.debug("Avvio della scansione...")

                # Esegui la scansione e ottieni la lista dei dispositivi
                dispositivi = self.scanner.scan()
                numero_dispositivi = len(dispositivi)

                # Se non ci sono dispositivi, mostra un messaggio e chiudi la finestra
                if numero_dispositivi == 0:
                    informazioni = "Nessun dispositivo trovato sulla rete"
                    messagebox.showinfo("Risultato Scansione", informazioni)
                else:
                    self.modello.aggiungi_bean(Costanti.DISPOSITIVI, dispositivi)
                    self.logger.debug(f"Dispositivi aggiunti: {dispositivi}")

                    # Aggiorna la vista dopo la scansione
                    if self.vista_principale:
                        self.vista_principale.carica_dispositivi()
                        self.vista_principale.aggiorna_info()

                # Simulazione del progresso, qui incrementiamo la progress bar in base al numero di dispositivi
                for i in range(1, numero_dispositivi + 1):
                    # Calcola la percentuale di progresso
                    progresso = (i / numero_dispositivi) * 100
                    self.progress["value"] = progresso
                    self.dialogo.update_idletasks()  # Aggiorna la GUI
                    threading.Event().wait(0.1)  # Aggiungi un piccolo ritardo per aggiornare la progress bar

            finally:
                # Ferma la progress bar e chiudi la finestra di dialogo
                self.progress["value"] = 100
                self.dialogo.destroy()

        # Avvia la scansione in un thread separato per non bloccare l'interfaccia grafica
        threading.Thread(target=esegui_scansione, daemon=True).start()

    def centra_progress(self, finestra, larghezza, altezza):
        """Centra la finestra rispetto alla finestra principale."""
        finestra_principale = self.vista_principale.master # La finestra principale
        finestra_principale.update_idletasks()  # Aggiorna le dimensioni

        # Calcola la posizione
        x_pos = finestra_principale.winfo_x() + (finestra_principale.winfo_width() // 2) - (larghezza // 2)
        y_pos = finestra_principale.winfo_y() + (finestra_principale.winfo_height() // 2) - (altezza // 2)

        # Imposta la geometria della finestra
        finestra.geometry(f"{larghezza}x{altezza}+{x_pos}+{y_pos}")
