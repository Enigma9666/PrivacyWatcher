import os
import sys
from datetime import datetime
from scanner.scanner import scan_file
from report.report_generator import generate_txt_report

# Importa la funzione per lanciare l'interfaccia grafica
from GUI.gui_app import launch_gui
from db.database import inizializza_db

# Inizializza il database SQLite all'avvio dell'applicazione
inizializza_db()

def check_environment():
    """
    Verifica l'ambiente di esecuzione e mostra un avviso se non è un sistema Unix-like.
    Sebbene il software possa funzionare su altri sistemi, è ottimizzato per GNU/Linux.
    """
    if os.name != 'posix':
        print("Attenzione: questo software è progettato per sistemi GNU/Linux o Unix-like.")
    else:
        print("Ambiente GNU/Linux rilevato. Avvio dell'applicazione...")

def group_results(results):
    """
    Raggruppa i risultati della scansione per tipo di dato sensibile.
    
    Args:
        results (list): Lista dei risultati dalla scansione
        
    Returns:
        dict: Dizionario con i risultati raggruppati per tipo di dato
    """
    grouped = {}
    for item in results:
        key = item['data_type']
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped

def main_cli(path):
    """
    Esegue la scansione in modalità command line interface (CLI).
    
    Args:
        path (str): Percorso del file da scansionare
    """
    # Esegue la scansione del file specificato
    results = scan_file(path)

    # Se non sono stati trovati risultati, mostra messaggio di successo
    if not results:
        print("\n✅ Nessun dato sensibile rilevato.")
        return

    # Mostra i risultati della scansione
    print("\n== RISULTATI DELLA SCANSIONE ==\n")
    for r in results:
        print(f"📄 File: {r['file']}")
        print(f"🔢 Riga: {r['line']}")
        print(f"🔍 Contenuto: {r['content'].strip()}")
        print(f"   → {r['data_type']}: {r['match']}\n")

    # Chiede all'utente se vuole generare un report
    risposta = input("Vuoi generare un report .txt dei risultati? (s/n): ").lower()
    if risposta == 's':
        # Raggruppa i risultati per tipo di dato
        grouped = group_results(results)
        
        # Genera un nome file con timestamp
        timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        filename = f"Report_{timestamp}.txt"
        
        # Genera il report
        generate_txt_report(grouped, path, filename)
        print(f"📄 Report generato: {filename}")

def main():
    """
    Funzione principale che determina la modalità di esecuzione del programma.
    
    Modalità disponibili:
    - --gui: Avvia l'interfaccia grafica
    - <percorso_file>: Esegue la scansione CLI del file specificato
    """
    # Verifica l'ambiente di esecuzione
    check_environment()

    # Controlla gli argomenti della riga di comando
    if len(sys.argv) == 2 and sys.argv[1] == '--gui':
        # Avvia l'interfaccia grafica
        print("Avvio modalità grafica...")
        launch_gui()
    elif len(sys.argv) == 2:
        # Esegue la scansione CLI del file specificato
        print("Esecuzione della modalità test senza GUI.")
        main_cli(sys.argv[1])
    else:
        # Mostra le istruzioni d'uso
        print("Uso: python3 main.py <percorso_file> oppure python3 main.py --gui")

# Punto di ingresso del programma
if __name__ == "__main__":
    main()
