import os
import sys
from utils.patterns import patterns
from utils.validator import validate_luhn


def scan_line_for_sensitive_data(line):
    findings = []
    for label, pattern in patterns.items():
        matches = pattern.findall(line)
        if matches:
            # Validazione per carte di credito
            if label == "Carta di Credito":
                valid_matches = [m for m in matches if validate_luhn(m)]
                if valid_matches:
                    findings.append((label, valid_matches))
            else:
                findings.append((label, matches))
    return findings


def scan_file(file_path):
    results = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for lineno, line in enumerate(lines, start=1):
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
    return results


def scan_directory(directory):
    report = []
    for root, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                report.extend(scan_file(full_path))
    return report


def print_report(results):
    if not results:
        print("Nessun dato sensibile trovato.")
        return

    print("== RISULTATI DELLA SCANSIONE ==")
    for match in results:
        print(f"\n📄 File: {match['file']}")
        print(f"🔢 Riga: {match['line']}")
        print(f"🔍 Contenuto: {match['content']}")
        print(f"   → {match['data_type']}: {match['match']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 scanner.py <file_o_directory_da_scansionare>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        results = scan_file(path)
    elif os.path.isdir(path):
        results = scan_directory(path)
    else:
        print(f"[!] Il percorso specificato non è un file né una directory valida: {path}")
        sys.exit(1)

    print_report(results)
