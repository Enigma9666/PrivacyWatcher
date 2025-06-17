import sqlite3
import os
import json
from datetime import datetime

# Percorso del database
DB_PATH = os.path.join("data", "logs.db")

def inizializza_db():
    """Crea il database e la tabella scansioni, se non esistono."""
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
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
        # Se la colonna "stato" non esiste (DB già creato), la aggiunge
        try:
            cursor.execute("ALTER TABLE scansioni ADD COLUMN stato TEXT")
        except sqlite3.OperationalError:
            pass  # La colonna esiste già, ignora errore
        conn.commit()

inizializza_db()

def salva_scansione(directory: str, risultati: list, report_name: str, stato: str):
    """Salva una nuova scansione nel database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risultati_json = json.dumps(risultati, indent=2)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scansioni (timestamp, report_name, directory, risultati, stato, percorso)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, report_name, directory, risultati_json, stato))
        conn.commit()

def recupera_report():
    """Restituisce lista di tuple: (timestamp, report_name, stato, percorso)"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, report_name, stato
            FROM scansioni
            ORDER BY timestamp DESC
        """)
        return cursor.fetchall()

def recupera_contenuto_report(report_name: str):
    """Recupera il contenuto JSON di una scansione dal nome del report."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT risultati FROM scansioni
            WHERE report_name = ?
            LIMIT 1
        """, (report_name,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None
