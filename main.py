import os
import sys
from datetime import datetime
from scanner.scanner import scan_file
from report.report_generator import generate_txt_report

# 👇 Import della GUI
from GUI.gui_app import launch_gui

def check_environment():
    if os.name != 'posix':
        print("Attenzione: questo software è progettato per sistemi GNU/Linux o Unix-like.")
    else:
        print("Ambiente GNU/Linux rilevato. Avvio dell'applicazione...")

def group_results(results):
    grouped = {}
    for item in results:
        key = item['data_type']
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped

def main_cli(path):
    results = scan_file(path)

    if not results:
        print("\n✅ Nessun dato sensibile rilevato.")
        return

    print("\n== RISULTATI DELLA SCANSIONE ==\n")
    for r in results:
        print(f"📄 File: {r['file']}")
        print(f"🔢 Riga: {r['line']}")
        print(f"🔍 Contenuto: {r['content'].strip()}")
        print(f"   → {r['data_type']}: {r['match']}\n")

    risposta = input("Vuoi generare un report .txt dei risultati? (s/n): ").lower()
    if risposta == 's':
        grouped = group_results(results)
        timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        filename = f"Report_{timestamp}.txt"
        generate_txt_report(grouped, path, filename)
        print(f"📄 Report generato: {filename}")

def main():
    check_environment()

    if len(sys.argv) == 2 and sys.argv[1] == '--gui':
        print("Avvio modalità grafica...")
        launch_gui()
    elif len(sys.argv) == 2:
        print("Esecuzione della modalità test senza GUI.")
        main_cli(sys.argv[1])
    else:
        print("Uso: python3 main.py <percorso_file> oppure python3 main.py --gui")


if __name__ == "__main__":
    main()
