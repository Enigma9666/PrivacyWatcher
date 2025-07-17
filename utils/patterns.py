import re

# Dizionario contenente i pattern regex per identificare diversi tipi di dati sensibili
patterns = {
    # Pattern per identificare indirizzi email
    # Riconosce il formato standard: nome@dominio.estensione
    "Email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", re.IGNORECASE),
    
    # Pattern per numeri di telefono italiani e internazionali
    # Supporta: prefisso +39, numeri fissi, cellulari, numeri internazionali
    "Telefono": re.compile(r"""
        (?:
            (?:\+39\s?)?                    # Prefisso italiano opzionale
            (?:0\d{1,4}[\s\-]?)?           # Prefisso urbano opzionale
            \d{6,11}                        # Numero principale
            |
            (?:\+39\s?)?                   # Prefisso italiano opzionale
            3\d{2}[\s\-]?\d{6,7}           # Cellulare italiano
            |
            (?:\+\d{1,3}[\s\-]?)?          # Prefisso internazionale generico
            \d{6,15}                        # Numero internazionale
        )
    """, re.VERBOSE),
    
    # Pattern per codice fiscale italiano
    # Formato: 6 lettere + 2 cifre + 1 lettera + 2 cifre + 1 lettera + 3 cifre + 1 lettera
    "Codice Fiscale": re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", re.IGNORECASE),
    
    # Pattern per codici IBAN europei
    # Formato: 2 lettere (paese) + 2 cifre (controllo) + codice bancario specifico per paese
    "IBAN": re.compile(r"""
        \b
        (?:IT|DE|FR|ES|GB|US|NL|BE|AT|CH|PT|GR|IE|FI|LU|MT|CY|EE|LV|LT|SI|SK|PL|CZ|HU|HR|RO|BG|DK|SE|NO)
        \d{2}
        [A-Z0-9]{4}
        \d{7}
        [A-Z0-9]{12}
        \b
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per password
    # Cerca variazioni di "password", "pwd", "pass" seguiti da ":" o "=" e il valore
    "Password": re.compile(r"""
        (?:
            (?:password|pwd|pass|psw|passwd|parola_chiave|chiave)
            \s*[:=]\s*
            (?:["']?)([^\s"']{4,})(?:["']?)
        )
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per numeri di carte di credito
    # Supporta: Visa, MasterCard, American Express, Discover e formato generico 16 cifre
    "Carta di Credito": re.compile(r"""
        \b
        (?:
            4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4} |    # Visa
            5[1-5]\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4} |  # MasterCard
            3[47]\d{1,2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{3} |  # American Express
            6(?:011|5\d{2})[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4} | # Discover
            \d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}        # Generico 16 cifre
        )
        \b
    """, re.VERBOSE),
    
    # Pattern per Partita IVA italiana
    # Formato: "P.IVA" o "P IVA" seguiti da 11 cifre
    "Partita IVA": re.compile(r"\bP\.?\s*IVA:?\s*(\d{11})\b", re.IGNORECASE),
    
    # Pattern per codice sanitario (tessera sanitaria)
    # Formato: 3 lettere + 3 cifre + 1 lettera + 2 cifre
    "Codice Sanitario": re.compile(r"\b[A-Z]{3}\s*\d{3}\s*[A-Z]\d{2}\b", re.IGNORECASE),
    
    # Pattern per documenti di identità
    # Supporta: carta d'identità, passaporto, patente
    "Numero Documento": re.compile(r"""
        (?:
            (?:carta\s+(?:d')?identità|CI|documento)\s*(?:n\.?|numero)?\s*:?\s*([A-Z]{2}\d{7}) |
            (?:passaporto|passport)\s*(?:n\.?|numero)?\s*:?\s*([A-Z]{2}\d{7}) |
            (?:patente)\s*(?:n\.?|numero)?\s*:?\s*([A-Z]{2}\d{7}[A-Z])
        )
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per indirizzi stradali italiani
    # Riconosce: via, viale, piazza, corso, ecc. seguiti da nome e numero civico
    "Indirizzo": re.compile(r"""
        (?:
            (?:via|viale|piazza|corso|largo|vicolo|strada)\s+
            [A-Za-z\s]{2,30}\s*
            (?:,?\s*\d{1,4})?
            (?:\s*[-–]\s*\d{5}\s+[A-Za-z\s]+)?
        )
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per Codice di Avviamento Postale (CAP)
    # Formato: 5 cifre
    "CAP": re.compile(r"\b\d{5}\b"),
    
    # Pattern per coordinate bancarie
    # Supporta: ABI, CAB, CIN, SWIFT, BIC
    "Coordinate Bancarie": re.compile(r"""
        (?:
            ABI\s*[:=]\s*\d{5} |
            CAB\s*[:=]\s*\d{5} |
            CIN\s*[:=]\s*[A-Z] |
            SWIFT\s*[:=]\s*[A-Z]{8,11} |
            BIC\s*[:=]\s*[A-Z]{8,11}
        )
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per indirizzi IP
    # Formato IPv4: 4 gruppi di 1-3 cifre (0-255) separati da punti
    "IP Address": re.compile(r"""
        \b
        (?:
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
        )
        \b
    """, re.VERBOSE),
    
    # Pattern per numeri previdenziali
    # Supporta: INPS, INAIL, numeri pensionistici
    "Numero Previdenziale": re.compile(r"""
        (?:
            (?:codice\s+)?(?:inps|inail|pensione)\s*[:=]\s*\d{8,12} |
            (?:numero\s+)?(?:previdenziale|pensionistico)\s*[:=]\s*\d{8,12}
        )
    """, re.VERBOSE | re.IGNORECASE),
    
    # Pattern per codice fiscale aziendale
    # Formato: 11 cifre (uguale alla partita IVA per le aziende)
    "Codice Fiscale Azienda": re.compile(r"\b\d{11}\b(?=.*(?:codice\s+fiscale|CF|P\.?\s*IVA))", re.IGNORECASE),
}
