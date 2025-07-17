import ttkbootstrap as tb                      # Wrapper di tkinter con tema moderno
from ttkbootstrap.constants import *           # Costanti usate in ttkbootstrap (es. tb.END)
from tkinter import filedialog, messagebox, scrolledtext  # Dialoghi e widget standard
import tkinter as tk
from tkinter import ttk
import os
import datetime
from scanner.scanner import scan_file, scan_directory  # Funzioni per scannerizzare file/cartelle
from report.report_generator import generate_txt_report  # Funzione per generare report testuali
from db.database import salva_scansione, recupera_report, recupera_contenuto_report, elimina_report  # DB

import tkinter.ttk as classic_ttk
import tkcalendar.dateentry
tkcalendar.dateentry.ttk.Entry = classic_ttk.Entry  # Patch per usare tkcalendar con ttk.Entry classico
from tkcalendar import DateEntry                    # Widget calendario per selezione date

class PrivacyWatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PrivacyWatcher - GUI")
        self.root.geometry("1000x700")   # Dimensione finestra iniziale
        self.root.minsize(800, 600)      # Dimensione minima finestra

        self.path = tb.StringVar()  # Variabile stringa per il percorso selezionato
        self.results = []           # Lista risultati scannerizzazione

        self.create_widgets()       # Costruisce interfaccia grafica

    def create_widgets(self):
        # Frame superiore con campo testo per percorso e bottone Sfoglia
        path_frame = tb.Frame(self.root)
        path_frame.pack(fill='x', padx=20, pady=10)

        tb.Entry(path_frame, textvariable=self.path, width=70).pack(side='left', expand=True, fill='x', padx=5)
        tb.Button(path_frame, text="Sfoglia", command=self.browse_path, bootstyle="secondary").pack(side='left', padx=5)

        # Frame per i pulsanti principali: scannerizza, esporta report, apri database
        button_frame = tb.Frame(self.root)
        button_frame.pack(pady=10)

        tb.Button(button_frame, text="Avvia scannerizzazione", command=self.run_scan, bootstyle="success").pack(side='left', padx=5)
        tb.Button(button_frame, text="Esporta Report", command=self.export_report, bootstyle="info").pack(side='left', padx=5)
        tb.Button(button_frame, text="Database", command=self.open_database_window, bootstyle="primary").pack(side='left', padx=5)

        # Area di testo scrollabile dove mostrare i risultati della scansione
        self.text_area = scrolledtext.ScrolledText(self.root, wrap='word', font=("Courier New", 10))
        self.text_area.pack(fill='both', expand=True, padx=20, pady=10)

    def browse_path(self):
        # Permette all'utente di scegliere un file o una directory da scannerizzare
        path = filedialog.askopenfilename()
        if not path:
            path = filedialog.askdirectory()
        if path:
            self.path.set(path)  # Imposta il percorso selezionato nel campo di testo

    def run_scan(self):
        # Pulisce area testo e ottiene percorso da scannerizzare
        self.text_area.delete(1.0, tb.END)
        path = self.path.get()

        if not path:
            messagebox.showwarning("Attenzione", "Seleziona un file o una directory da scansionare.")
            return

        # Scansiona file o directory a seconda del tipo
        if os.path.isfile(path):
            self.results = scan_file(path)
        elif os.path.isdir(path):
            self.results = scan_directory(path)
        else:
            messagebox.showerror("Errore", "Percorso non valido.")
            return

        # Se nessun dato sensibile trovato, lo segnala
        if not self.results:
            self.text_area.insert(tb.END, "✅ Nessun dato sensibile rilevato.")
        else:
            # Altrimenti mostra i dettagli di ogni elemento trovato
            for item in self.results:
                self.text_area.insert(tb.END, f"📄 File: {item['file']}\n")
                self.text_area.insert(tb.END, f"🔢 Riga: {item['line']}\n")
                self.text_area.insert(tb.END, f"🔍 Contenuto: {item['content']}\n")
                self.text_area.insert(tb.END, f"   → {item['data_type']}: {item['match']}\n\n")

        # Salva la scansione nel database con nome report basato su timestamp
        timestamp = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        report_name = f"Report_{timestamp}.txt"
        salva_scansione(path, self.results, report_name, "Scannerizzato")

    def export_report(self):
        # Esporta i risultati attuali in un file report testuale strutturato
        if not self.results:
            messagebox.showinfo("Nessun risultato", "Nessun dato da esportare.")
            return

        # Organizza i dati per tipo di dato sensibile
        structured = {}
        for item in self.results:
            dtype = item['data_type']
            structured.setdefault(dtype, []).append({
                "file": item['file'],
                "match": item['match']
            })

        # Genera nome file con timestamp
        timestamp = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        filename = f"Report_{timestamp}.txt"
        filepath = os.path.join("reports", filename)

        # Genera file report e salva anche nel database (stato "Esportato")
        generate_txt_report(structured, self.path.get(), filepath)
        salva_scansione(self.path.get(), self.results, filename, "Esportato")

        messagebox.showinfo("Report generato", f"Report salvato in {filename}")

    def open_database_window(self):
        # Apre una nuova finestra che mostra lo storico dei report salvati nel database
        # Se finestra già aperta la porta in primo piano
        if hasattr(self, 'db_win') and self.db_win.winfo_exists():
            self.db_win.lift()
            return
    
        # Recupera tutti i report salvati
        self.records = recupera_report()
    
        self.db_win = tb.Toplevel(self.root)
        self.db_win.focus_force()
        self.db_win.title("Storico Report")
        self.db_win.geometry("900x600")
    
        def on_close():
            self.db_win.destroy()
            del self.db_win
    
        self.db_win.protocol("WM_DELETE_WINDOW", on_close)

        # Sezione ricerca e filtro
        top_frame = tb.Frame(self.db_win)
        top_frame.pack(fill="x", padx=10, pady=5)

        search_var = tb.StringVar()
        tb.Label(top_frame, text="Cerca:").pack(side="left", padx=5)
        search_entry = tb.Entry(top_frame, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Treeview per mostrare i report con colonne per Percorso, Nome, Data, Stato
        tree = tb.Treeview(self.db_win, columns=("Percorso", "Nome", "Data", "Stato"), show="headings", bootstyle="info")
        for col in ("Percorso", "Nome", "Data", "Stato"):
            tree.heading(col, text=col)
        tree.column("Percorso", width=200)
        tree.column("Nome", width=200)
        tree.column("Data", width=180)
        tree.column("Stato", width=100)
        tree.pack(padx=10, pady=10, fill='both', expand=True)

        # Doppio click su un record apre una finestra con il contenuto dettagliato del report
        def show_report(event):
            item_id = tree.identify_row(event.y)
            if not item_id:
                return

            values = tree.item(item_id, "values")
            report_name = values[1]
            results = recupera_contenuto_report(report_name)
            if results is None:
                messagebox.showerror("Errore", "Report non trovato nel database.")
                return

            view_win = tb.Toplevel(self.db_win)
            view_win.title(f"Contenuto - {report_name}")
            view_win.geometry("700x500")

            text_area = scrolledtext.ScrolledText(view_win, wrap='word')
            text_area.pack(fill='both', expand=True)

            # Mostra dettagli della scansione in modo leggibile e disabilita l'editing
            for item in results:
                text_area.insert(tb.END, f"📄 File: {item['file']}\n")
                text_area.insert(tb.END, f"🔢 Riga: {item['line']}\n")
                text_area.insert(tb.END, f"🔍 Contenuto: {item['content']}\n")
                text_area.insert(tb.END, f"   → {item['data_type']}: {item['match']}\n\n")
            text_area.config(state='disabled')

        tree.bind("<Double-1>", show_report)

        # Frame per filtri data inizio/fine (con entry di testo per date)
        filter_frame = tk.Frame(self.db_win)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        label_start = tk.Label(filter_frame, text="Data inizio:")
        label_start.pack(side='left', padx=(0, 5))
        
        start_date = tb.Entry(filter_frame, width=12)
        start_date.pack(side='left', padx=(0, 15))
        
        label_end = tk.Label(filter_frame, text="Data fine:")
        label_end.pack(side='left', padx=(0, 5))
        
        end_date = tb.Entry(filter_frame, width=12)
        end_date.pack(side='left', padx=(0, 15))

        # Applica filtro di ricerca per data (con parsing date e controlli)
        def apply_date_filter():
            from datetime import datetime
            try:
                dt_start = datetime.strptime(start_date.get(), "%m/%d/%y")
                dt_end = datetime.strptime(end_date.get(), "%m/%d/%y")
            except ValueError:
                messagebox.showerror("Errore", "Formato data non valido.")
                return

            if dt_start > dt_end:
                messagebox.showerror("Errore", "La data di inizio deve essere precedente a quella di fine.")
                return

            filtered = []
            for ts, name, stato, percorso in self.records:
                try:
                    ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    if dt_start <= ts_dt <= dt_end:
                        filtered.append((ts, name, stato, percorso))
                except ValueError:
                    continue
            populate_list(filtered)

        # Ricarica dati da database e aggiorna lista report
        def aggiorna_dati():
            self.records = recupera_report()
            populate_list()

        # Elimina report selezionato dopo conferma utente
        def elimina_report_selezionato():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona un report da eliminare.")
                return
            item = tree.item(selected[0])
            report_name = item['values'][1]
            conferma = messagebox.askyesno("Conferma eliminazione", f"Vuoi davvero eliminare il report '{report_name}'?")
            if conferma:
                elimina_report(report_name)
                messagebox.showinfo("Eliminato", f"Il report '{report_name}' è stato eliminato.")
                aggiorna_dati()

        # Pulsanti filtro e elimina
        tb.Button(filter_frame, text="Applica filtro", command=apply_date_filter, bootstyle="info").pack(side='left', padx=10)
        tb.Button(self.db_win, text="Elimina report selezionato", command=elimina_report_selezionato, bootstyle="danger").pack(pady=5)

        # Funzione per popolare la treeview filtrando per testo di ricerca
        def populate_list(filtered_records=None, filter_text=""):
            tree.delete(*tree.get_children())
            data = filtered_records if filtered_records is not None else self.records
            for ts, name, stato, percorso in data:
                short_path = os.path.basename(percorso)
                if filter_text.lower() in f"{short_path} {name} {ts} {stato}".lower():
                    tree.insert("", tb.END, values=(short_path, name, ts, stato))

        # Aggiorna filtro ricerca testo dinamicamente
        search_var.trace_add("write", lambda *args: populate_list(filter_text=search_var.get()))
        populate_list()


def launch_gui():
    # Funzione per lanciare la GUI principale con tema 'cosmo'
    root = tb.Window(themename="cosmo")
    root.title("PrivacyWatcher")
    root.geometry("1000x700")

    # Callback chiusura finestra principale
    def on_close():
        print("Uscita dalla GUI richiesta...")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Inizializza la GUI custom
    PrivacyWatcherGUI(root)

    root.mainloop()
