import socket
import subprocess
import tkinter as tk
from datetime import time
from tkinter import ttk, messagebox
import socket
import struct
import time
from scapy.all import *
import argparse
from pyvis.network import Network
from scapy.layers.inet import traceroute, UDP, IP
from tkinterhtml import HtmlFrame
from modello.costanti import Costanti
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
        self.modello = modello

    def azione_bottone_traceroute(self):
        self.vista_principale.nascondi_componenti_scansione()
        self.vista_principale.mostra_componenti_traceroute()
        # Forza l'aggiornamento del layout dopo aver mostrato i componenti
        self.vista_principale.update_idletasks()
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

                # Mostra la finestra di dialogo mentre il traceroute è in corso
                self.vista_principale.mostra_finestra_dialogo("Traceroute in corso",
                                                              f"Traceroute verso {target} in corso, attendere...")

                # Esegui la scansione del traceroute
                self.scan_traceroute(target)

                # Una volta completata la scansione, chiudi la finestra di dialogo
                self.vista_principale.chiudi_finestra_dialogo()

                # Una volta che i dati sono stati aggiornati nel modello, aggiorna la tabella dei risultati
                self.vista_principale.aggiorna_tabella_risultati()

            except Exception as e:
                # Gestisci le eccezioni: chiudi la finestra di dialogo e mostra il messaggio di errore
                self.vista_principale.chiudi_finestra_dialogo()  # Chiude la finestra di dialogo se c'è un errore
                self.vista_principale.mostra_messaggio_errore("Errore", f"Si è verificato un errore: {e}")

        # Crea un thread per eseguire la scansione senza bloccare la GUI
        thread = threading.Thread(target=esegui_traceroute)
        thread.start()  # Avvia il thread

    def scan_traceroute(self, target):
        if not target:
            # Se il campo dell'indirizzo è vuoto, mostra solo l'errore e ferma l'esecuzione
            self.vista_principale.mostra_messaggio_errore("Errore", "Il campo indirizzo non può essere vuoto.")
            return  # Ferma l'esecuzione senza proseguire

        # Verifica se il target è risolvibile tramite DNS
        try:
            socket.gethostbyname(target)  # Prova a risolvere l'IP dal nome di dominio
        except socket.gaierror:
            self.vista_principale.mostra_messaggio_errore("Errore di Connessione",
                                                          "Indirizzo non valido o non trovato.")
            return  # Ferma l'esecuzione se il nome non può essere risolto

        maxTTL = 50  # Numero massimo di hop
        targetIP = target  # Imposta il target dell'indirizzo IP

        # Inizializza la lista per i risultati
        self.lista_traceroute = []

        try:
            ttl = 1
            while ttl <= maxTTL:
                # Crea il pacchetto con TTL crescente
                ip_packet = IP(dst=targetIP, ttl=ttl)
                udp_packet = UDP(dport=33434)  # Porta 33434 usata per traceroute
                packet = ip_packet / udp_packet

                # Invia il pacchetto e ricevi la risposta
                reply = sr1(packet, timeout=2, verbose=0)  # Timeout di 2 secondi

                # Stampa il TTL attuale
                print(f"TTL[{ttl}]> ", end="")

                if reply is None:
                    # Nessuna risposta, stampa * * *
                    print("* * *")
                    break  # Fermati subito se non c'è risposta
                elif reply.type == 3:
                    # Risposta ricevuta e destinazione raggiunta
                    print(f"{reply.src}")
                    ip = reply.src
                    # Calcola il tempo di risposta
                    tempo_ms = (reply.time - packet.sent_time) * 1000  # Calcolo del tempo in ms

                    # Risolvi l'hostname e la regione
                    hostname = self._get_hostname(ip) if ip else "N/D"
                    regione = self._get_regione(ip) if ip else "N/D"

                    # Crea un oggetto Traceroute per questo hop
                    risultato = Traceroute(ttl, ip, hostname, tempo_ms, regione)
                    self.lista_traceroute.append(risultato)

                    # Se il pacchetto ha raggiunto il target, termina il ciclo
                    if ip == targetIP:
                        break
                    else:
                        print("Nessuna risposta valida dopo 1 hop")
                        break  # Se la risposta è al localhost (127.0.0.1) o non valida, fermati subito
                else:
                    # Risposta intermedia
                    print(f"{reply.src}")
                    ip = reply.src
                    # Calcola il tempo di risposta
                    tempo_ms = (reply.time - packet.sent_time) * 1000  # Calcolo del tempo in ms

                    # Risolvi l'hostname e la regione
                    hostname = self._get_hostname(ip) if ip else "N/D"
                    regione = self._get_regione(ip) if ip else "N/D"

                    # Crea un oggetto Traceroute per questo hop
                    risultato = Traceroute(ttl, ip, hostname, tempo_ms, regione)
                    self.lista_traceroute.append(risultato)

                ttl += 1  # Incrementa il TTL per il prossimo hop

            if not self.lista_traceroute:
                # Se non ci sono risultati, mostra un errore
                self.vista_principale.mostra_messaggio_errore("Errore", "Nessun risultato trovato per il traceroute.")
                return

            # Aggiungi la lista completa al modello, utilizzando la chiave 'Traceroute'
            self.modello.aggiungi_bean("Traceroute", self.lista_traceroute)

            # Una volta che i dati sono stati aggiornati nel modello, aggiorna la tabella dei risultati
            self.vista_principale.aggiorna_tabella_risultati()

        except socket.gaierror as e:  # Gestisci l'errore di nome non valido
            self.vista_principale.mostra_messaggio_errore("Errore di Connessione",
                                                          "Indirizzo non valido o non trovato.")
            print(f"Errore di connessione: {e}")
            return  # Ferma l'esecuzione se si verifica un errore di rete

        except Exception as e:
            # Gestisci altre eccezioni generiche
            self.vista_principale.mostra_messaggio_errore(
                "Errore durante il traceroute",
                f"Si è verificato un errore: {e}"
            )
            return  # Ferma l'esecuzione se si verifica un errore generico

    def _get_hostname(self, ip):
        try:
            from socket import gethostbyaddr
            return gethostbyaddr(ip)[0]
        except:
            return "N/D"

    def _get_regione(self, ip):
        try:
            details = self.ipinfo_handler.getDetails(ip)
            regione = details.region
            return regione if regione else "Sconosciuta"
        except Exception as e:
            print(f"Errore nella risoluzione della regione per IP {ip}: {e}")
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
        router = None
        for dispositivo in dispositivi:
            if dispositivo["Tipologia"] == 'Router':
                print("Router collegato al centro")
                router = dispositivo
                break

        if router:
            # Se il router viene trovato, aggiungilo come nodo centrale
            net.add_node(router["IP"], label=f"Router\nIP: {router['IP']}\nMAC: {router['MAC']}", color="red", size=30,
                         icon="fa fa-cogs")

            # Aggiungi gli altri dispositivi come nodi e collegali al router
            for dispositivo in dispositivi:
                if dispositivo != router:  # Escludi il router
                    net.add_node(dispositivo["IP"],
                                 label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                                 color="lightblue", size=20, icon="fa fa-desktop")
                    net.add_edge(router["IP"], dispositivo["IP"])  # Collegamento al router

        else:
            # Se il router non è stato trovato, aggiungi i nodi e collega tutti i dispositivi tra loro
            for dispositivo in dispositivi:
                net.add_node(dispositivo["IP"],
                             label=f"IP: {dispositivo['IP']}\nMAC: {dispositivo['MAC']}\nSO: {dispositivo['Sistema Operativo']}",
                             color="lightgreen", size=20, icon="fa fa-desktop")

            # Collega tutti i dispositivi tra loro
            for i in range(len(dispositivi)):
                for j in range(i + 1, len(dispositivi)):
                    net.add_edge(dispositivi[i]["IP"], dispositivi[j]["IP"])

        # Salva il grafo come file HTML
        output_path = os.path.abspath("grafo_interattivo.html")
        net.save_graph(output_path)

        return output_path

    def azione_avvia_scansione(self):
        self.vista_principale.mostra_componenti_scansione()
        # Crea la finestra di dialogo modale
        titolo = "Scansione in corso"
        etichetta = "Scansione in corso..."
        self.vista_principale.mostra_finestra_dialogo(titolo,etichetta)
        # Funzione per avviare la scansione in un thread separato
        def esegui_scansione():
            try:
                self.logger.debug("Avvio della scansione...")
                dispositivi = self.scanner.scan()
                if len(dispositivi) == 0:
                    self.vista_principale.chiudi_finestra_dialogo()
                    informazioni = (
                        "Nessun dispositivo trovato sulla rete"
                    )
                    messagebox.showinfo("Risultato Scansione", informazioni)
                else:
                    self.modello.aggiungi_bean(Costanti.DISPOSITIVI, dispositivi)
                    self.logger.debug(f"Dispositivi aggiunti: {dispositivi}")

                    # Aggiorna la vista dopo la scansione
                    if self.vista_principale:
                        self.vista_principale.carica_dispositivi()
                        self.vista_principale.aggiorna_info()
            finally:
                # Chiude la finestra di dialogo dopo la scansione
                self.vista_principale.chiudi_finestra_dialogo()

        # Avvia la scansione in un thread separato per non bloccare l'interfaccia grafica
        threading.Thread(target=esegui_scansione, daemon=True).start()

