import os
import datetime

def generate_txt_report(results: dict, scan_path: str, filename: str):
    """
    Genera un report in formato .txt contenente i risultati della scansione.
    results: dizionario con dati sensibili trovati
    scan_path: percorso scansionato
    filename: nome file di output del report (senza path)
    """

    # Definisce la directory in cui salvare il report: una cartella "report" nella directory corrente
    report_dir = os.path.join(os.getcwd(), "report")
    # Costruisce il percorso completo del file di report, dentro la cartella "report"
    filepath = os.path.join("report", filename)
    # Crea la cartella "report" se non esiste già, per evitare errori nel salvataggio
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Apre (o crea) il file di testo per scrivere il report, con codifica UTF-8
    with open(filepath, 'w', encoding='utf-8') as f:
        # Intestazione generale del report
        f.write(f"Report di scansione PrivacyWatcher\n")
        f.write(f"Data e ora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Percorso scansionato: {scan_path}\n")
        f.write("="*50 + "\n\n")  # Linea divisoria

        total_found = 0  # Variabile per contare il totale delle occorrenze trovate

        # Ciclo su tutti i tipi di dati sensibili trovati
        for data_type, occurrences in results.items():
            count = len(occurrences)  # Numero di occorrenze per il tipo corrente
            total_found += count      # Aggiorna il totale complessivo
            # Scrive il tipo di dato e il numero di occorrenze trovate
            f.write(f"{data_type} - Totale occorrenze: {count}\n")
            # Per ogni occorrenza, scrive file e valore trovato
            for item in occurrences:
                f.write(f"  File: {item['file']}\n")
                f.write(f"  Valore trovato: {item['match']}\n")
                f.write("\n")
            f.write("-"*50 + "\n")  # Separatore dopo ogni tipo di dato

        # Alla fine scrive il totale generale delle occorrenze trovate
        f.write(f"\nTotale occorrenze trovate: {total_found}\n")

        # Se non sono stati trovati dati sensibili, scrive un messaggio specifico
        if total_found == 0:
            f.write("Nessun dato sensibile rilevato.\n")

    # Stampa a console un messaggio informativo con il percorso del file salvato
    print(f"[INFO] Report salvato nel file: {filepath}")
