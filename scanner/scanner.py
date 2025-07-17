import os
import sys
from utils.patterns import patterns  # Importa i pattern regex per i dati sensibili
from utils.validator import validate_luhn, validate_italian_cf, validate_iban, validate_italian_phone  # Funzioni di validazione specifiche
from db.database import salva_scansione  # Funzione per salvare la scansione nel DB (non usata nel codice mostrato)

# Funzione che scansiona una singola riga di testo alla ricerca di dati sensibili
def scan_line_for_sensitive_data(line):
    findings = []  # Lista dei risultati trovati in questa riga
    
    # Cicla sui tipi di dato sensibile e sui relativi pattern regex
    for label, pattern in patterns.items():
        matches = pattern.findall(line)  # Cerca tutte le occorrenze nel testo
        
        if matches:
            validated_matches = []  # Lista di match che passano la validazione
            
            for match in matches:
                # Se il match è una tupla (da gruppi regex), prendi il primo elemento non vuoto
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                
                # Rimuovi spazi e caratteri speciali per la validazione
                clean_match = match.replace(' ', '').replace('-', '').replace('.', '')
                
                # Controlla la validità in base al tipo di dato
                if label == "Carta di Credito":
                    if validate_luhn(clean_match):
                        validated_matches.append(match)
                elif label == "Codice Fiscale":
                    if validate_italian_cf(clean_match.upper()):
                        validated_matches.append(match)
                elif label == "IBAN":
                    if validate_iban(clean_match.upper()):
                        validated_matches.append(match)
                elif label == "Telefono":
                    if validate_italian_phone(clean_match):
                        validated_matches.append(match)
                elif label == "Email":
                    # Validazione base: deve contenere '@' e un '.' dopo la chiocciola
                    if '@' in match and '.' in match.split('@')[1]:
                        validated_matches.append(match)
                elif label == "Password":
                    # Filtra password troppo comuni o troppo corte
                    if len(clean_match) >= 4 and clean_match.lower() not in ['password', 'pass', 'pwd', '1234', 'admin']:
                        validated_matches.append(match)
                elif label == "CAP":
                    # CAP italiano valido tra 00010 e 98168 e di 5 cifre
                    if clean_match.isdigit() and len(clean_match) == 5 and 10 <= int(clean_match) <= 98168:
                        validated_matches.append(match)
                elif label == "Partita IVA":
                    # Controlla che sia un numero di 11 cifre
                    if clean_match.isdigit() and len(clean_match) == 11:
                        validated_matches.append(match)
                elif label == "IP Address":
                    # Per IP, la validazione è già gestita dal regex
                    validated_matches.append(match)
                else:
                    # Per altri tipi, accetta se almeno 3 caratteri
                    if len(clean_match) >= 3:
                        validated_matches.append(match)
            
            # Se ci sono match validati, aggiungili ai risultati
            if validated_matches:
                findings.append((label, validated_matches))
    
    return findings  # Ritorna lista di tuple (tipo dato, lista di match)

# Funzione che scansiona un singolo file alla ricerca di dati sensibili
def scan_file(file_path):
    results = []
    
    # Controlla che il file esista
    if not os.path.exists(file_path):
        print(f"[!] Il file {file_path} non esiste.")
        return results
    
    # Controlla la dimensione del file, evita file > 50 MB
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            print(f"[!] Il file {file_path} è troppo grande (>{file_size/1024/1024:.1f}MB). Saltato.")
            return results
    except OSError:
        print(f"[!] Errore nell'accesso al file {file_path}")
        return results
    
    # Estensioni di file considerate per la scansione
    processable_extensions = {'.txt', '.csv', '.log', '.conf', '.cfg', '.ini', '.xml', '.json', '.py', '.js', '.html', '.css', '.sql', '.md', '.rst'}
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Se estensione non nota, prova a leggere e verifica se è testo o binario
    if file_ext not in processable_extensions and file_ext:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                test_lines = f.readlines(1000)  # Legge fino a 1000 caratteri
                # Se trova caratteri non ASCII (oltre 127), probabilmente binario
                if any(ord(c) > 127 for line in test_lines for c in line[:100]):
                    print(f"[!] Il file {file_path} sembra essere binario. Saltato.")
                    return results
        except:
            print(f"[!] Impossibile leggere il file {file_path}. Saltato.")
            return results
    
    # Prova a leggere il file riga per riga
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
            for lineno, line in enumerate(lines, start=1):
                # Salta righe vuote o troppo lunghe (>10.000 caratteri)
                if not line.strip() or len(line) > 10000:
                    continue
                
                matches = scan_line_for_sensitive_data(line)
                if matches:
                    # Per ogni risultato trovato, salva i dettagli
                    for label, values in matches:
                        for value in values:
                            results.append({
                                "file": file_path,
                                "line": lineno,
                                "content": line.strip(),
                                "data_type": label,
                                "match": value
                            })
                            
    # Gestione errori di encoding, prova encoding latin-1 se utf-8 fallisce
    except UnicodeDecodeError:
        print(f"[!] Errore di codifica nel file {file_path}. Tentativo con encoding alternativo...")
        try:
            with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                lines = f.readlines()
                for lineno, line in enumerate(lines, start=1):
                    if not line.strip() or len(line) > 10000:
                        continue
                    matches = scan_line_for_sensitive_data(line)
                    if matches:
                        for label, values in matches:
                            for value in values:
                                results.append({
                                    "file": file_path,
                                    "line": lineno,
                                    "content": line.strip(),
                                    "data_type": label,
                                    "match": value
                                })
        except Exception as e:
            print(f"[!] Errore nella lettura di {file_path}: {e}")
    except Exception as e:
        print(f"[!] Errore nella lettura di {file_path}: {e}")
    
    return results  # Ritorna lista di dizionari con i risultati trovati

# Funzione per scansionare una directory ricorsivamente
def scan_directory(directory):
    report = []
    scanned_files = 0
    skipped_files = 0
    
    print(f"[INFO] Inizio scansione della directory: {directory}")
    
    # Cammina ricorsivamente dentro la directory
    for root, dirs, files in os.walk(directory):
        # Esclude directory comuni da saltare (git, cache, editor config...)
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.svn', 'node_modules', '.idea', '.vscode'}]
        
        for filename in files:
            full_path = os.path.join(root, filename)
            
            # Salta file temporanei o di sistema
            if filename.startswith('.') or filename.endswith(('.tmp', '.temp', '.bak', '.swp')):
                skipped_files += 1
                continue
            
            if os.path.isfile(full_path):
                file_results = scan_file(full_path)  # Scansiona singolo file
                if file_results:
                    report.extend(file_results)  # Aggiungi risultati al report totale
                    print(f"[FOUND] {len(file_results)} risultati in {full_path}")
                scanned_files += 1
                
                # Stampa progresso ogni 100 file
                if scanned_files % 100 == 0:
                    print(f"[INFO] Scansionati {scanned_files} file...")
    
    print(f"[INFO] Scansione completata: {scanned_files} file processati, {skipped_files} file saltati")
    print(f"[INFO] Trovati {len(report)} risultati totali")
    
    return report  # Ritorna la lista completa dei risultati

# Funzione per stampare a video i risultati della scansione in modo leggibile
def print_report(results):
    if not results:
        print("✅ Nessun dato sensibile trovato.")
        return

    print("\n== RISULTATI DELLA SCANSIONE ==")
    
    # Raggruppa per tipo di dato
    by_type = {}
    for result in results:
        data_type = result['data_type']
        if data_type not in by_type:
            by_type[data_type] = []
        by_type[data_type].append(result)
    
    # Mostra statistiche
    print(f"\n📊 STATISTICHE:")
    for data_type, items in by_type.items():
        print(f"  {data_type}: {len(items)} occorrenze")
    
    print(f"\n🔍 DETTAGLI:")
    for result in results:
        print(f"\n📄 File: {result['file']}")
        print(f"🔢 Riga: {result['line']}")
        print(f"🔍 Contenuto: {result['content']}")
        print(f"   → {result['data_type']}: {result['match']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 scanner.py <file_o_directory_da_scansionare>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        results = scan_file(path)
        print_report(results)
    elif os.path.isdir(path):
        results = scan_directory(path)
        print_report(results)
    else:
        print(f"[!] Il percorso specificato non è un file né una directory valida: {path}")
        sys.exit(1)
