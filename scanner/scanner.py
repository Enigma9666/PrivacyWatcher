import os
import sys
from utils.patterns import patterns
from utils.validator import validate_luhn, validate_italian_cf, validate_iban, validate_italian_phone
from db.database import salva_scansione

def scan_line_for_sensitive_data(line):
    """
    Scansiona una singola riga di testo alla ricerca di dati sensibili.
    
    Args:
        line (str): Riga di testo da scansionare
        
    Returns:
        list: Lista di tuple (tipo_dato, matches_validi) trovati nella riga
    """
    findings = []
    
    # Itera attraverso tutti i pattern definiti
    for label, pattern in patterns.items():
        matches = pattern.findall(line)
        if matches:
            validated_matches = []
            
            for match in matches:
                # Se il match è una tupla (da gruppi regex), prendi il primo elemento non vuoto
                if isinstance(match, tuple):
                    match = next((m for m in match if m), match[0])
                
                # Pulisce il match da spazi e caratteri speciali per la validazione
                clean_match = match.replace(' ', '').replace('-', '').replace('.', '')
                
                # Validazione specifica per ogni tipo di dato
                if label == "Carta di Credito":
                    # Usa l'algoritmo di Luhn per validare carte di credito
                    if validate_luhn(clean_match):
                        validated_matches.append(match)
                elif label == "Codice Fiscale":
                    # Valida il codice fiscale italiano
                    if validate_italian_cf(clean_match.upper()):
                        validated_matches.append(match)
                elif label == "IBAN":
                    # Valida l'IBAN usando l'algoritmo modulo 97
                    if validate_iban(clean_match.upper()):
                        validated_matches.append(match)
                elif label == "Telefono":
                    # Valida numeri di telefono italiani
                    if validate_italian_phone(clean_match):
                        validated_matches.append(match)
                elif label == "Email":
                    # Validazione base per email
                    if '@' in match and '.' in match.split('@')[1]:
                        validated_matches.append(match)
                elif label == "Password":
                    # Esclude password troppo comuni o troppo corte
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
            
            # Aggiunge i risultati validati alla lista
            if validated_matches:
                findings.append((label, validated_matches))
    
    return findings
