import os
import sys
from utils.patterns import patterns
from utils.validator import validate_luhn, validate_italian_cf, validate_iban, validate_italian_phone
from db.database import salva_scansione

def scan_line_for_sensitive_data(line):
    findings = []
    
    for label, pattern in patterns.items():
        matches = pattern.findall(line)
        if matches:
            validated_matches = []
            
            for match in matches:
                # Se il match è una tupla (da gruppi regex), prendi il primo elemento non vuoto
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                
                # Pulisci il match da spazi e caratteri speciali per la validazione
                clean_match = match.replace(' ', '').replace('-', '').replace('.', '')
                
                # Validazione specifica per tipo di dato
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
                    # Validazione base per email
                    if '@' in match and '.' in match.split('@')[1]:
                        validated_matches.append(match)
                elif label == "Password":
                    # Per le password, controlliamo che non siano troppo comuni
                    if len(clean_match) >= 4 and clean_match.lower() not in ['password', 'pass', 'pwd', '1234', 'admin']:
                        validated_matches.append(match)
                elif label == "CAP":
                    # Validazione CAP italiano (00010-98168)
                    if clean_match.isdigit() and len(clean_match) == 5 and 10 <= int(clean_match) <= 98168:
                        validated_matches.append(match)
                elif label == "Partita IVA":
                    # Validazione base partita IVA (11 cifre)
                    if clean_match.isdigit() and len(clean_match) == 11:
                        validated_matches.append(match)
                elif label == "IP Address":
                    # Validazione IP già gestita dal regex
                    validated_matches.append(match)
                else:
                    # Per altri tipi, accetta il match se supera controlli base
                    if len(clean_match) >= 3:
                        validated_matches.append(match)
            
            if validated_matches:
                findings.append((label, validated_matches))
    
    return findings

def scan_file(file_path):
    results = []
    
    # Controlla se il file è leggibile
    if not os.path.exists(file_path):
        print(f"[!] Il file {file_path} non esiste.")
        return results
    
    # Controlla la dimensione del file (evita file troppo grandi)
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50 MB
            print(f"[!] Il file {file_path} è troppo grande (>{file_size/1024/1024:.1f}MB). Saltato.")
            return results
    except OSError:
        print(f"[!] Errore nell'accesso al file {file_path}")
        return results
    
    # Estensioni di file da processare
    processable_extensions = {'.txt', '.csv', '.log', '.conf', '.cfg', '.ini', '.xml', '.json', '.py', '.js', '.html', '.css', '.sql', '.md', '.rst'}
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Se non è un'estensione conosciuta, prova comunque ma con gestione errori più robusta
    if file_ext not in processable_extensions and file_ext:
        try:
            # Test di lettura di poche righe per vedere se è testo
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                test_lines = f.readlines(1000)  # Leggi solo i primi 1000 caratteri
                if any(ord(c) > 127 for line in test_lines for c in line[:100]):
                    print(f"[!] Il file {file_path} sembra essere binario. Saltato.")
                    return results
        except:
            print(f"[!] Impossibile leggere il file {file_path}. Saltato.")
            return results
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
            for lineno, line in enumerate(lines, start=1):
                # Salta linee vuote o troppo lunghe
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
    
    return results

def scan_directory(directory):
    report = []
    scanned_files = 0
    skipped_files = 0
    
    print(f"[INFO] Inizio scansione della directory: {directory}")
    
    for root, dirs, files in os.walk(directory):
        # Salta alcune directory comuni da evitare
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.svn', 'node_modules', '.idea', '.vscode'}]
        
        for filename in files:
            full_path = os.path.join(root, filename)
            
            # Salta file temporanei e di sistema
            if filename.startswith('.') or filename.endswith(('.tmp', '.temp', '.bak', '.swp')):
                skipped_files += 1
                continue
            
            if os.path.isfile(full_path):
                file_results = scan_file(full_path)
                if file_results:
                    report.extend(file_results)
                    print(f"[FOUND] {len(file_results)} risultati in {full_path}")
                scanned_files += 1
                
                # Mostra progresso ogni 100 file
                if scanned_files % 100 == 0:
                    print(f"[INFO] Scansionati {scanned_files} file...")
    
    print(f"[INFO] Scansione completata: {scanned_files} file processati, {skipped_files} file saltati")
    print(f"[INFO] Trovati {len(report)} risultati totali")
    
    return report

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
