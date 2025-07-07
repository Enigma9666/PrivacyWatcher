import tkinter as ttk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from scanner.scanner import scan_file, scan_directory
from report.report_generator import generate_txt_report
from db.database import salva_scansione, recupera_report, recupera_contenuto_report
import datetime
from tkcalendar import DateEntry

class PrivacyWatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PrivacyWatcher - GUI")
        self.root.geometry("700x500")

        self.path = tk.StringVar()
        self.results = []

        self.create_widgets()

    def create_widgets(self):
        # Frame per il percorso
        path_frame = tk.Frame(self.root)
        path_frame.pack(fill='x', padx=10, pady=5)

        tk.Entry(path_frame, textvariable=self.path, width=60).pack(side='left', padx=5)
        tk.Button(path_frame, text="Sfoglia", command=self.browse_path).pack(side='left')

        # Frame per i pulsanti
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Avvia scannerizzazione", command=self.run_scan, bg="#4CAF50", fg="white").pack(side='left', padx=5)
        tk.Button(button_frame, text="Esporta Report", command=self.export_report).pack(side='left', padx=5)
        tk.Button(button_frame, text="Database", command=self.open_database_window).pack(side='left', padx=5)

        # Area di testo scrollabile
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=5)



    def browse_path(self):
        path = filedialog.askopenfilename()
        if not path:
            path = filedialog.askdirectory()
        if path:
            self.path.set(path)

    def run_scan(self):
        self.text_area.delete(1.0, tk.END)
        path = self.path.get()

        if not path:
            messagebox.showwarning("Attenzione", "Seleziona un file o una directory da scansionare.")
            return

        if os.path.isfile(path):
            self.results = scan_file(path)
        elif os.path.isdir(path):
            self.results = scan_directory(path)
        else:
            messagebox.showerror("Errore", "Percorso non valido.")
            return

        if not self.results:
            self.text_area.insert(tk.END, "✅ Nessun dato sensibile rilevato.")
        else:
            for item in self.results:
                self.text_area.insert(tk.END, f"📄 File: {item['file']}\n")
                self.text_area.insert(tk.END, f"🔢 Riga: {item['line']}\n")
                self.text_area.insert(tk.END, f"🔍 Contenuto: {item['content']}\n")
                self.text_area.insert(tk.END, f"   → {item['data_type']}: {item['match']}\n\n")

        # Salvataggio automatico della scansione nel database
        # import datetime
        # from db.database import salva_scansione, recupera_report, recupera_contenuto_report
 

        timestamp = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        report_name = f"Report_{timestamp}.txt"
        salva_scansione(path, self.results, report_name, "Scannerizzato")

    def export_report(self):
        if not self.results:
            messagebox.showinfo("Nessun risultato", "Nessun dato da esportare.")
            return

        structured = {}
        for item in self.results:
            dtype = item['data_type']
            structured.setdefault(dtype, []).append({
                "file": item['file'],
                "match": item['match']
            })

        timestamp = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        filename = f"Report_{timestamp}.txt"
        filepath = os.path.join("reports", filename)

        generate_txt_report(structured, self.path.get(), filepath)

        # Salva anche nel database
        """salva_scansione(self.path.get(), self.results, filename)"""
        salva_scansione(self.path.get(), self.results, filename, "Esportato")


        messagebox.showinfo("Report generato", f"Report salvato in {filename}")

    def open_database_window(self):
        records = recupera_report()  # (timestamp, report_name)

        db_win = tk.Toplevel(self.root)
        db_win.title("Storico Report")
        db_win.geometry("700x500")

        # ───── Cerca per nome o data
        top_frame = tk.Frame(db_win)
        top_frame.pack(fill="x", padx=10, pady=5)

        search_var = tk.StringVar()
        tk.Label(top_frame, text="Cerca:").pack(side="left", padx=5)
        search_entry = tk.Entry(top_frame, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        listbox = tk.Listbox(db_win, width=130, font=("Courier", 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def populate_list(filter_text=""):
            listbox.delete(0, tk.END)
            for ts, name, stato, percorso in records:
                short_path = os.path.basename(percorso)
                # entry = f"{short_path:<25} | {name:<30} | {ts:<20} | {stato}"
                entry = f"{percorso:<25} | {name:<30} | {ts} | {stato}"
                if filter_text.lower() in entry.lower():
                    listbox.insert(tk.END, entry)


        populate_list()

        def on_search(*args):
            populate_list(search_var.get())
        search_var.trace_add("write", on_search)

        def show_report(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                selected = listbox.get(idx)
                report_name = selected.split("|")[1].strip()

                results = recupera_contenuto_report(report_name)
                if results is None:
                    messagebox.showerror("Errore", "Report non trovato nel database.")
                    return

                view_win = tk.Toplevel(db_win)
                view_win.title(f"Contenuto - {report_name}")
                view_win.geometry("700x500")

                text_area = scrolledtext.ScrolledText(view_win, wrap=tk.WORD)
                text_area.pack(fill=tk.BOTH, expand=True)

                for item in results:
                    text_area.insert(tk.END, f"📄 File: {item['file']}\n")
                    text_area.insert(tk.END, f"🔢 Riga: {item['line']}\n")
                    text_area.insert(tk.END, f"🔍 Contenuto: {item['content']}\n")
                    text_area.insert(tk.END, f"   → {item['data_type']}: {item['match']}\n\n")

                text_area.config(state=tk.DISABLED)

        listbox.bind("<<ListboxSelect>>", show_report)
        filter_frame = ttk.Frame(db_win)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Data inizio:").pack(side=tk.LEFT, padx=(0,5))
        start_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2025)
        start_date.pack(side=tk.LEFT, padx=(0,15))

        ttk.Label(filter_frame, text="Data fine:").pack(side=tk.LEFT, padx=(0,5))
        end_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2025)
        end_date.pack(side=tk.LEFT, padx=(0,15))

        def apply_date_filter():
            # Prendo le date e converto in datetime
            dt_start = datetime.strptime(start_date.get(), "%m/%d/%y")
            dt_end = datetime.strptime(end_date.get(), "%m/%d/%y")
            if dt_start > dt_end:
                messagebox.showerror("Errore", "La data di inizio deve essere precedente alla data di fine.")
                return
        
            # Filtro i record in base al range
            filtered = []
            for ts, name, stato in records:
                # ts è stringa, converto in datetime
                dt_record = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                if dt_start <= dt_record <= dt_end:
                    filtered.append((ts, name, stato))
        
            populate_list(filtered)

        filter_btn = ttk.Button(filter_frame, text="Applica filtro", command=apply_date_filter)
        filter_btn.pack(side=tk.LEFT)

        # --- modifica la funzione populate_list per accettare lista di record come argomento ---
        def populate_list(filtered_records=None, filter_text=""):
            listbox.delete(0, tk.END)
            if filtered_records is None:
                filtered_records = records
            for ts, name, stato in filtered_records:
                entry = f"{name:<35} | {ts} | {stato}"
                if filter_text.lower() in entry.lower():
                    listbox.insert(tk.END, entry)

        populate_list()




def launch_gui():
    root = tk.Tk()
    app = PrivacyWatcherGUI(root)
    root.mainloop()
