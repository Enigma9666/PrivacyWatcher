import sqlite3
import os
import json
from datetime import datetime

# Percorso del database
DB_PATH = os.path.join("data", "logs.db")



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
"""def salva_scansione(path, risultati):
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

# Recupera tutte le scansioni salvate"""

def salva_scansione(path, risultati, report_name):
    inizializza_db()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for item in risultati:
            cursor.execute("""
                INSERT INTO scansioni (timestamp, report_name, directory, data_type, file_path, match)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                report_name,
                path,
                item.get("data_type", ""),
                item.get("file", ""),
                item.get("match", "")
            ))
        conn.commit()


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

def export_report(self):
    if not self.results:
        messagebox.showinfo("Nessun risultato", "Nessun dato da esportare.")
        return

    structured = {}
    for item in self.results:
        dtype = item['data_type']
        if dtype not in structured:
            structured[dtype] = []
        structured[dtype].append({"file": item['file'], "match": item['match']})

    timestamp = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
    filename = f"Report_{timestamp}.txt"
    filepath = os.path.join("reports", filename)
    generate_txt_report(structured, self.path.get(), filepath)
    salva_scansione(self.path.get(), self.results, filename)
    messagebox.showinfo("Report generato", f"Report salvato in {filename}")


inizializza_db()
