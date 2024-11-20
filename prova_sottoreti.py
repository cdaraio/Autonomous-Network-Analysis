from pysnmp.hlapi import *


def get_routing_table(router_ip, community='public'):
    """
    Ottieni la tabella di routing da un router utilizzando SNMP.

    Args:
        router_ip (str): Indirizzo IP del router.
        community (str): Nome della community SNMP (default: 'public').

    Returns:
        list: Una lista di tuple contenenti le informazioni della tabella di routing.
    """
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((router_ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.4.21')),  # OID per la tabella di routing
        lexicographicMode=False
    )
    routing_table = []
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(f"Errore SNMP: {errorIndication}")
            break
        elif errorStatus:
            print(f"Errore SNMP: {errorStatus.prettyPrint()} at {errorIndex}")
            break
        else:
            for varBind in varBinds:
                routing_table.append(varBind)
    return routing_table


def main():
    """
    Punto di ingresso principale del programma.
    Richiede all'utente l'IP del router e la community SNMP,
    quindi recupera e stampa la tabella di routing.
    """
    router_ip = input("Inserisci l'IP del router: ")
    community = input("Inserisci la community SNMP (default: 'public'): ") or 'public'

    print(f"\nRecupero della tabella di routing dal router {router_ip}...\n")
    routing_table = get_routing_table(router_ip, community)

    if routing_table:
        print(f"Tabella di routing del router {router_ip}:")
        for entry in routing_table:
            print(entry)
    else:
        print(f"Nessuna voce trovata nella tabella di routing del router {router_ip}.")


if __name__ == "__main__":
    main()
