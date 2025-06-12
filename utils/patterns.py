import re

patterns = {
    "Email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "Telefono": re.compile(r"\+?\d{2,4}[ \-]?\d{6,12}"),
    "Codice Fiscale": re.compile(r"[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]"),
    "IBAN": re.compile(r"[A-Z]{2}\d{2}[A-Z0-9]{1,30}"),
    "Password": re.compile(r"(?:password|pwd)\s*[:=]\s*[\w\d@#$%^&+=!]{4,}"),
    "Carta di Credito": re.compile(r"(?:\d[ -]*?){13,16}"),
}
