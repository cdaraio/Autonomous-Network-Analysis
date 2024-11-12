import scapy.all as scapy
from modello.dispositivo import Dispositivo
from modello.enum_dispositivo import TipoDispositivo  # Importa l'Enum per il tipo di dispositivo

class ScannerRete:
    def __init__(self, logger):
        self.logger = logger  # Salviamo il logger per usarlo successivamente

    def get_ip_range(self):
        """Funzione per ottenere l'IP di destinazione e la subnet"""
        ip = scapy.get_if_addr(scapy.conf.iface)  # Usa l'interfaccia di rete predefinita
        subnet = ip.rsplit('.', 1)[0] + '.0/24'  # La subnet predefinita sarà della forma "x.x.x.0/24"
        return subnet

    def ping_ip(self, ip):
        """Funzione per eseguire un ping su un IP e ottenere una risposta"""
        risposta = scapy.sr1(scapy.IP(dst=ip)/scapy.ICMP(), timeout=1, verbose=False)
        return risposta

    def scan_dispositivi(self, ip_range):
        self.logger.info(f"Avvio scansione sulla rete: {ip_range}")
        dispositivi = []

        # Creiamo una richiesta ARP per tutti gli indirizzi IP nella subnet
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet per tutti gli indirizzi MAC
        richiesta_completa = broadcast/arp_request

        # Invia la richiesta ARP e ottieni tutte le risposte
        risposte = scapy.srp(richiesta_completa, timeout=3, verbose=False)[0]

        for risposta in risposte:
            ip = risposta[1].psrc  # IP del dispositivo che ha risposto
            mac = risposta[1].hwsrc  # MAC del dispositivo che ha risposto

            dispositivo = Dispositivo(
                ip=ip,  # Indirizzo IP del dispositivo
                mac=mac,  # Indirizzo MAC
                tipo_dispositivo=TipoDispositivo.CLIENT,  # Tipo di dispositivo (Client)
                so="Non disponibile",  # Sistema operativo (se non disponibile)
                nome_host="Non disponibile",  # Nome host (se non disponibile)
                tempo_risposta=0.0,  # Tempo di risposta (non disponibile con ARP)
                ttl=0,  # TTL (non disponibile con ARP)
                stato="Attivo"  # Stato del dispositivo
            )
            dispositivi.append(dispositivo)

            # Log delle informazioni del dispositivo trovato
            self.logger.info(f"Dispositivo trovato: {dispositivo}")

        return dispositivi

    def scan(self):
        """Funzione di scansione che avvia la rilevazione dei dispositivi sulla rete"""
        ip_range = self.get_ip_range()  # Ottieni il range di IP dalla tua rete
        dispositivi = self.scan_dispositivi(ip_range)  # Scansiona i dispositivi

        # Log dei dispositivi trovati
        self.logger.info(f"Totale dispositivi rilevati: {len(dispositivi)}")

