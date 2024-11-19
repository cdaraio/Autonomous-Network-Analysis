import scapy.all as scapy
from modello.dispositivo import Dispositivo
from modello.enum_dispositivo import TipoDispositivo
import socket
import time
import logging

class ScannerRete:
    def __init__(self, logger):
        self.logger = logger  # Salviamo il logger per usarlo successivamente

    def get_ip_range(self):
        """Funzione per ottenere l'IP di destinazione e la subnet"""
        ip = scapy.get_if_addr(scapy.conf.iface)  # Usa l'interfaccia di rete predefinita
        subnet = ip.rsplit('.', 1)[0] + '.0/24'  # La subnet predefinita sarà della forma "x.x.x.0/24"
        self.logger.info(f"Range IP ottenuto: {subnet}")
        return subnet

    def ping_ip(self, ip):
        """Funzione per eseguire un ping su un IP e ottenere una risposta"""
        risposta = scapy.sr1(scapy.IP(dst=ip)/scapy.ICMP(), timeout=1, verbose=False)
        return risposta

    def scan_ports(self, ip, port_range=[80, 443, 22, 21, 51820]):
        """Scansiona le porte aperte per un dato IP e associa il servizio alla porta aperta"""
        servizi_attivi = {}
        for porta in port_range:
            self.logger.info(f"Scansione della porta {porta} su {ip}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                risultato = sock.connect_ex((ip, porta))
                self.logger.info(f"Risultato: {risultato}")
                if risultato == 0:  # Porta aperta
                    try:
                        servizio = socket.getservbyport(porta)
                    except OSError:  # Se il servizio non è conosciuto
                        servizio = "Servizio sconosciuto"
                    servizi_attivi[porta] = servizio
                    self.logger.info(f"Porta aperta trovata: {porta} ({servizio})")
                elif risultato != 0:
                    self.logger.warning(f"Porta {porta} su {ip} non raggiungibile, codice di errore: {risultato}")
        return servizi_attivi

    def scan_dispositivi(self, ip_range):
        self.logger.info(f"Avvio scansione sulla rete: {ip_range}")
        dispositivi = []

        # Creiamo una richiesta ARP per tutti gli indirizzi IP nella subnet
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet per tutti gli indirizzi MAC
        richiesta_completa = broadcast / arp_request

        # Invia la richiesta ARP e ottieni tutte le risposte
        risposte = scapy.srp(richiesta_completa, timeout=3, verbose=False)[0]

        # Log per mostrare il numero di risposte ARP ricevute
        self.logger.info(f"Numero di risposte ARP ricevute: {len(risposte)}")

        for risposta in risposte:
            ip = risposta[1].psrc  # IP del dispositivo che ha risposto
            mac = risposta[1].hwsrc  # MAC del dispositivo che ha risposto

            # Ottenere informazioni aggiuntive (TTL, sistema operativo, tempo di risposta)
            try:
                start_time = time.time()  # Registra il tempo di partenza
                risposta_ping = scapy.sr1(scapy.IP(dst=ip) / scapy.ICMP(), timeout=1, verbose=False)
                if risposta_ping:
                    ttl = risposta_ping.ttl  # Time to Live dal pacchetto ICMP
                    tempo_risposta = time.time() - start_time  # Calcola il tempo di risposta
                    sistema_operativo = self.deduce_os(ttl)  # Metodo per dedurre il sistema operativo in base al TTL
                else:
                    ttl = "Sconosciuto"
                    tempo_risposta = "Non disponibile"
                    sistema_operativo = "Sconosciuto"

                # Eseguire la scansione delle porte per ottenere i servizi attivi
                servizi_attivi = self.scan_ports(ip)

                dispositivo = {
                    'IP': ip,
                    'MAC': mac,
                    'Sistema Operativo': sistema_operativo,
                    'TTL': ttl,
                    'Tempo di Risposta': f"{tempo_risposta:.4f} s" if isinstance(tempo_risposta,
                                                                                 float) else tempo_risposta,
                    'Servizi Attivi': servizi_attivi
                }
                dispositivi.append(dispositivo)
                self.logger.info(f"Dispositivo trovato: {dispositivo}")
            except Exception as e:
                self.logger.error(f"Errore durante la scansione di {ip}: {e}")

        return dispositivi

    def deduce_os(self, ttl):
        """Metodo per dedurre il sistema operativo in base al TTL osservato"""
        if ttl >= 128:
            return "Sistema Windows (possibile)"
        elif ttl <= 64:
            return "Sistema Unix/Linux (possibile)"
        else:
            return "Sistema operativo sconosciuto"

    def scan(self):
        """Funzione di scansione che avvia la rilevazione dei dispositivi sulla rete"""
        ip_range = self.get_ip_range()  # Ottieni il range di IP dalla tua rete
        dispositivi = self.scan_dispositivi(ip_range)  # Scansiona i dispositivi

        # Log del totale dei dispositivi trovati
        self.logger.info(f"Numero totale di dispositivi rilevati: {len(dispositivi)}")
        if len(dispositivi) == 0:
            self.logger.warning("Nessun dispositivo trovato nella rete.")

