import os
import datetime

def generate_txt_report(results: dict, scan_path: str, filename: str):
    """
    Genera un report in formato .txt contenente i risultati della scansione.
    results: dizionario con dati sensibili trovati
    scan_path: percorso scansionato
    filename: nome file di output del report (senza path)
    """

    # Aggiunta: salva sempre il report nella directory 'report'
    report_dir = os.path.join(os.getcwd(), "reports")
    filepath = os.path.join("reports", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Report di scansione PrivacyWatcher\n")
        f.write(f"Data e ora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Percorso scansionato: {scan_path}\n")
        f.write("="*50 + "\n\n")

        total_found = 0

        for data_type, occurrences in results.items():
            count = len(occurrences)
            total_found += count
            f.write(f"{data_type} - Totale occorrenze: {count}\n")
            for item in occurrences:
                f.write(f"  File: {item['file']}\n")
                f.write(f"  Valore trovato: {item['match']}\n")
                f.write("\n")
            f.write("-"*50 + "\n")

        f.write(f"\nTotale occorrenze trovate: {total_found}\n")

        if total_found == 0:
            f.write("Nessun dato sensibile rilevato.\n")

    print(f"[INFO] Report salvato nel file: {filepath}")
