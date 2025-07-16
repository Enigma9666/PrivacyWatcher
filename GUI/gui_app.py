import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import os
from scanner.scanner import scan_file, scan_directory
from report.report_generator import generate_txt_report
from db.database import salva_scansione, recupera_report, recupera_contenuto_report, elimina_report
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

        tree = ttk.Treeview(db_win, columns=("Percorso", "Nome", "Data", "Stato"), show="headings")
        tree.heading("Percorso", text="Percorso")
        tree.heading("Nome", text="Nome Report")
        tree.heading("Data", text="Data")
        tree.heading("Stato", text="Stato")

        tree.column("Percorso", width=200)
        tree.column("Nome", width=200)
        tree.column("Data", width=150)
        tree.column("Stato", width=100)

        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # tree.bind("<<TreeviewSelect>>", show_report)


        def populate_list(filter_text=""):
            tree.delete(*tree.get_children())
            for ts, name, stato, percorso in records:
                short_path = os.path.basename(percorso)
                # entry = f"{short_path:<25} | {name:<30} | {ts:<20} | {stato}"
                tree.insert("", tk.END, values=(short_path, name, ts, stato))


        populate_list()

        def on_search(*args):
            populate_list(search_var.get())
        search_var.trace_add("write", on_search)

        def show_report(event):
            selected_item = tree.selection()
            if not selected_item:
                return
        
            values = tree.item(selected_item[0], "values")
            report_name = values[1]  # nome report (es. Report_2025.07.10-12.52.17.txt)
        
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

        tree.bind("<<TreeviewSelect>>", show_report)
        filter_frame = ttk.Frame(db_win)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Data inizio:").pack(side=tk.LEFT, padx=(0,5))
        start_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2025)
        start_date.pack(side=tk.LEFT, padx=(0,15))

        ttk.Label(filter_frame, text="Data fine:").pack(side=tk.LEFT, padx=(0,5))
        end_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2025)
        end_date.pack(side=tk.LEFT, padx=(0,15))

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
            for ts, name, stato, percorso in records:
                try:
                    ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    if dt_start <= ts_dt <= dt_end:
                        filtered.append((ts, name, stato, percorso))
                except ValueError:
                    continue  # Ignora i record con timestamp malformati
            populate_list(filtered)
        def aggiorna_dati():
            nonlocal records
            records = recupera_report()
            populate_list()
    
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


        filter_btn = ttk.Button(filter_frame, text="Applica filtro", command=apply_date_filter)
        filter_btn.pack(side=tk.LEFT)
        delete_btn = tk.Button(db_win, text="Elimina report selezionato", bg="red", fg="white", command=elimina_report_selezionato)
        delete_btn.pack(pady=5)


        # --- modifica la funzione populate_list per accettare lista di record come argomento ---
        def populate_list(filtered_records=None, filter_text=""):
            tree.delete(*tree.get_children())
            if filtered_records is None:
                filtered_records = records
            for ts, name, stato, percorso in filtered_records:
                short_path = os.path.basename(percorso)
                if filter_text.lower() in f"{short_path} {name} {ts} {stato}".lower():
                    tree.insert("", tk.END, values=(short_path, name, ts, stato))

        populate_list()

        



def launch_gui():
    root = tk.Tk()
    app = PrivacyWatcherGUI(root)
    root.mainloop()
