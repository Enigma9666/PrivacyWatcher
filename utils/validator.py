import re

def validate_luhn(card_number):
    """
    Valida un numero di carta di credito usando l'algoritmo di Luhn.
    
    L'algoritmo di Luhn è un metodo di controllo per verificare l'integrità
    dei numeri di carta di credito.
    
    Args:
        card_number (str): Numero di carta di credito da validare
        
    Returns:
        bool: True se il numero è valido, False altrimenti
    """
    # Estrae solo le cifre dal numero
    digits = [int(d) for d in card_number if d.isdigit()]
    
    # Controlla che la lunghezza sia nel range valido per carte di credito
    if len(digits) < 13 or len(digits) > 19:
        return False
    
    checksum = 0
    double = False
    
    # Processa le cifre da destra a sinistra
    for d in reversed(digits):
        if double:
            d *= 2
            # Se il risultato è maggiore di 9, sottrai 9
            if d > 9:
                d -= 9
        checksum += d
        double = not double
    
    # Il numero è valido se la somma è divisibile per 10
    return checksum % 10 == 0

def validate_italian_cf(codice_fiscale):
    """
    Valida un codice fiscale italiano.
    
    Controlla il formato e verifica la correttezza del carattere di controllo
    secondo l'algoritmo ufficiale italiano.
    
    Args:
        codice_fiscale (str): Codice fiscale da validare
        
    Returns:
        bool: True se il codice fiscale è valido, False altrimenti
    """
    if not codice_fiscale or len(codice_fiscale) != 16:
        return False
    
    # Controllo formato: 6 lettere + 2 cifre + 1 lettera + 2 cifre + 1 lettera + 3 cifre + 1 lettera
    if not re.match(r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$', codice_fiscale):
        return False
    
    # Tabelle per il calcolo del carattere di controllo
    # Valori per le posizioni dispari (1, 3, 5, ...)
    controllo_dispari = {
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19,
        'J': 21, 'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8,
        'S': 12, 'T': 14, 'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23,
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19,
        '9': 21
    }
    
    # Valori per le posizioni pari (2, 4, 6, ...)
    controllo_pari = {
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8,
        'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
        'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
    }
    
    # Calcola la somma secondo l'algoritmo
    somma = 0
    for i in range(15):
        char = codice_fiscale[i]
        if i % 2 == 0:  # Posizione dispari (1-based)
            somma += controllo_dispari.get(char, 0)
        else:  # Posizione pari (1-based)
            somma += controllo_pari.get(char, 0)
    
    # Calcola il carattere di controllo
    carattere_controllo = chr(65 + (somma % 26))
    return carattere_controllo == codice_fiscale[15]

def validate_iban(iban):
    """
    Valida un codice IBAN usando l'algoritmo di controllo modulo 97.
    
    Args:
        iban (str): Codice IBAN da validare
        
    Returns:
        bool: True se l'IBAN è valido, False altrimenti
    """
    if not iban or len(iban) < 15 or len(iban) > 34:
        return False
    
    # Rimuovi spazi e converti in maiuscolo
    iban = iban.replace(' ', '').upper()
    
    # Controllo formato base: 2 lettere + 2 cifre + caratteri alfanumerici
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
        return False
    
    # Sposta le prime 4 caratteri alla fine per il controllo
    rearranged = iban[4:] + iban[:4]
    
    # Sostituisci le lettere con i numeri corrispondenti (A=10, B=11, ..., Z=35)
    numeric_string = ''
    for char in rearranged:
        if char.isdigit():
            numeric_string += char
        else:
            numeric_string += str(ord(char) - ord('A') + 10)
    
    # Verifica usando il modulo 97 (deve essere 1 per IBAN validi)
    return int(numeric_string) % 97 == 1

def validate_italian_phone(phone):
    """
    Valida un numero di telefono italiano.
    
    Supporta numeri fissi, cellulari, numeri verdi e numeri internazionali.
    
    Args:
        phone (str): Numero di telefono da validare
        
    Returns:
        bool: True se il numero è valido, False altrimenti
    """
    if not phone:
        return False
    
    # Rimuovi spazi, trattini e altri caratteri non numerici (eccetto +)
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Controlli base sulla lunghezza
    if len(clean_phone) < 6 or len(clean_phone) > 15:
        return False
    
    # Gestione prefisso italiano
    if clean_phone.startswith('+39'):
        clean_phone = clean_phone[3:]
    elif clean_phone.startswith('0039'):
        clean_phone = clean_phone[4:]
    
    # Controllo lunghezza dopo rimozione prefisso
    if len(clean_phone) < 6 or len(clean_phone) > 11:
        return False
    
    # Cellulare italiano (inizia con 3)
    if clean_phone.startswith('3'):
        return len(clean_phone) == 10 and clean_phone[1] in '0123456789'
    
    # Numero fisso italiano (inizia con 0)
    if clean_phone.startswith('0'):
        return len(clean_phone) >= 8 and len(clean_phone) <= 11
    
    # Numero verde o servizi speciali
    if clean_phone.startswith(('800', '199', '166', '899')):
        return len(clean_phone) >= 6 and len(clean_phone) <= 10
    
    # Altri numeri internazionali
    if phone.startswith('+'):
        return len(clean_phone) >= 6 and len(clean_phone) <= 15
    
    return False

def validate_email(email):
    """
    Valida un indirizzo email.
    
    Args:
        email (str): Indirizzo email da validare
        
    Returns:
        bool: True se l'email è valida, False altrimenti
    """
    if not email or len(email) > 254:
        return False
    
    # Controllo formato base usando regex
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    
    # Controllo lunghezza delle parti locale e dominio
    local, domain = email.split('@')
    if len(local) > 64 or len(domain) > 253:
        return False
    
    # Controllo caratteri non permessi (punti consecutivi, inizio/fine con punto)
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    return True

def validate_italian_zip(cap):
    """
    Valida un CAP (Codice di Avviamento Postale) italiano.
    
    Args:
        cap (str): CAP da validare
        
    Returns:
        bool: True se il CAP è valido, False altrimenti
    """
    if not cap or not cap.isdigit() or len(cap) != 5:
        return False
    
    cap_int = int(cap)
    # Range valido per CAP italiani: 00010-98168
    return 10 <= cap_int <= 98168

def validate_italian_vat(partita_iva):
    """
    Valida una partita IVA italiana.
    
    Controlla il formato e verifica la cifra di controllo.
    
    Args:
        partita_iva (str): Partita IVA da validare
        
    Returns:
        bool: True se la partita IVA è valida, False altrimenti
    """
    if not partita_iva or not partita_iva.isdigit() or len(partita_iva) != 11:
        return False
    
    # Calcolo della cifra di controllo per partita IVA italiana
    somma = 0
    for i in range(10):
        cifra = int(partita_iva[i])
        if i % 2 == 0:  # Posizioni pari (0-based)
            somma += cifra
        else:  # Posizioni dispari (0-based)
            somma += (cifra * 2) % 9 if cifra * 2 > 9 else cifra * 2
    
    # Calcola la cifra di controllo
    controllo = (10 - (somma % 10)) % 10
    return controllo == int(partita_iva[10])

def validate_ip_address(ip):
    """
    Valida un indirizzo IP versione 4.
    
    Args:
        ip (str): Indirizzo IP da validare
        
    Returns:
        bool: True se l'IP è valido, False altrimenti
    """
    if not ip:
        return False
    
    # Divide l'IP in 4 parti separate da punti
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        # Ogni parte deve essere un numero tra 0 e 255
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False
