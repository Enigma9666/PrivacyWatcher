import sqlite3
import os
import json
from datetime import datetime

# Percorso del database
DB_PATH = os.path.join("data", "logs.db")

# Inizializza il database e crea la tabella se non esiste
"""def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scansioni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                path TEXT NOT NULL,
                risultati TEXT NOT NULL
            )
        """)
        conn.commit()"""

def inizializza_db():
    os.makedirs("data", exist_ok=True)  # Assicurati di creare la cartella prima
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scansioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            report_name TEXT,
            directory TEXT,
            data_type TEXT,
            file_path TEXT,
            match TEXT
        )
    """)
    conn.commit()
    conn.close()


# Salva una scansione nel database
def salva_scansione(path, risultati):
    inizializza_db()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risultati_json = json.dumps(risultati, indent=2)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scansioni (timestamp, path, risultati)
            VALUES (?, ?, ?)
        """, (timestamp, path, risultati_json))
        conn.commit()

# Recupera tutte le scansioni salvate
def leggi_scansioni():
    inizializza_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scansioni ORDER BY timestamp DESC")
        return cursor.fetchall()

def recupera_report():
    inizializza_db()
    conn = sqlite3.connect("data/logs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, report_name FROM scansioni ORDER BY timestamp DESC")
    records = cursor.fetchall()
    conn.close()
    return records

inizializza_db()
