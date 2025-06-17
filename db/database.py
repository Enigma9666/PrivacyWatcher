import sqlite3
import os
import json
from datetime import datetime

"""database.py – gestione persistente delle scansioni
────────────────────────────────────────────────────
• Ogni scansione (sia solo "Scannerizzata" che "Esportata") è registrata in una
  singola riga:  timestamp | report_name | directory | risultati(JSON) | stato
• Il JSON "risultati" contiene l'intera lista delle occorrenze trovate.
•  Le funzioni esposte sono:
    ─ inizializza_db()              → crea DB / tabella se mancante
    ─ salva_scansione(dir, res, nm, stato)
    ─ recupera_report()             → [(timestamp, report_name, stato), …]
    ─ recupera_contenuto_report(nm) → list(results)  o  None
"""

# Percorso del database ->  data/logs.db
DB_PATH = os.path.join("data", "logs.db")

# ──────────────────────────────────────────────────────────────
def inizializza_db() -> None:
    """Crea la cartella data/ e la tabella scansioni se non esistono."""
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scansioni (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT,
                report_name TEXT,
                directory   TEXT,
                risultati   TEXT,
                stato       TEXT
            )
            """
        )
        conn.commit()

# inizializza subito all'import
inizializza_db()

# ──────────────────────────────────────────────────────────────

def salva_scansione(directory: str, risultati: list, report_name: str, stato: str) -> None:
    """Registra/aggiorna una scansione.
    •  directory  → percorso analizzato
    •  risultati  → lista di dict, verrà salvata in JSON
    •  report_name→ "Report_<YYYY.MM.DD‑HH.MM.SS>.txt"
    •  stato      → "Scannerizzato"  |  "Esportato"
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risultati_json = json.dumps(risultati, indent=2, ensure_ascii=False)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO scansioni (timestamp, report_name, directory, risultati, stato)
            VALUES (?,?,?,?,?)
            """,
            (timestamp, report_name, directory, risultati_json, stato),
        )
        conn.commit()

# ──────────────────────────────────────────────────────────────

def recupera_report():
    """Ritorna lista di tuple  (timestamp, report_name, stato)  ordinate dal più recente."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT timestamp, report_name, stato
            FROM scansioni
            ORDER BY timestamp DESC
            """
        )
        return cur.fetchall()

# ──────────────────────────────────────────────────────────────

def recupera_contenuto_report(report_name: str):
    """Restituisce la lista risultati (deserialize JSON) di un report registrato.
    Se non trovato restituisce None."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT risultati FROM scansioni WHERE report_name = ? LIMIT 1",
            (report_name,),
        )
        row = cur.fetchone()
        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return []
        return None
