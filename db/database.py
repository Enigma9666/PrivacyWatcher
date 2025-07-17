import sqlite3       # Modulo per gestire database SQLite
import os            # Per operazioni su filesystem (cartelle, percorsi)
import json          # Per serializzare/desserializzare dati JSON
from datetime import datetime  # Per gestire date e orari

# Percorso del file database, dentro la cartella "data"
DB_PATH = os.path.join("data", "logs.db")

def inizializza_db():
    """Crea il database e la tabella scansioni se non esistono."""
    # Crea la cartella 'data' se non esiste già
    os.makedirs("data", exist_ok=True)
    
    # Connessione al database SQLite (il file viene creato se non esiste)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Crea la tabella 'scansioni' se non esiste, con colonne per:
        # id (chiave primaria autoincrement), timestamp, nome report, directory,
        # risultati (testo JSON), stato, percorso (stringhe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scansioni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                report_name TEXT,
                directory TEXT,
                risultati TEXT,
                stato TEXT,
                percorso TEXT
            )
        """)
        
        # Prova ad aggiungere la colonna "stato" se non esiste (per retrocompatibilità)
        try:
            cursor.execute("ALTER TABLE scansioni ADD COLUMN stato TEXT")
        except sqlite3.OperationalError:
            # Se la colonna esiste già, ignora l'errore
            pass
        
        conn.commit()  # Salva le modifiche nel DB

# Chiama la funzione per assicurarsi che il DB e la tabella siano pronti
inizializza_db()

def salva_scansione(directory: str, risultati: list, report_name: str, stato: str):
    """Salva una nuova scansione nel database."""
    # Ottieni timestamp corrente in formato leggibile
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Converte la lista di risultati in una stringa JSON indentata
    risultati_json = json.dumps(risultati, indent=2)

    # Connessione al DB e inserimento di un nuovo record nella tabella scansioni
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scansioni (timestamp, report_name, directory, risultati, stato, percorso)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, report_name, directory, risultati_json, stato, directory))
        conn.commit()  # Conferma inserimento

def recupera_report():
    """Restituisce la lista dei report (timestamp, nome, stato, percorso), ordinata per data decrescente."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, report_name, stato, percorso
            FROM scansioni
            ORDER BY timestamp DESC
        """)
        # Ritorna tutte le righe ottenute come lista di tuple
        return cursor.fetchall()

def recupera_contenuto_report(report_name: str):
    """Recupera i risultati JSON di una scansione dato il nome del report."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT risultati FROM scansioni
            WHERE report_name = ?
            LIMIT 1
        """, (report_name,))
        result = cursor.fetchone()
        if result:
            # Converte la stringa JSON in struttura dati Python e la restituisce
            return json.loads(result[0])
        # Se nessun risultato trovato, ritorna None
        return None

def elimina_report(report_name):
    """Elimina un report dal database dato il nome."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM scansioni WHERE report_name = ?", (report_name,))
        conn.commit()
