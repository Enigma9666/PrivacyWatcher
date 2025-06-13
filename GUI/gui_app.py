import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from scanner.scanner import scan_file, scan_directory
from report.report_generator import generate_txt_report
import datetime
from db.database import recupera_report

class PrivacyWatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PrivacyWatcher - GUI")
        self.root.geometry("700x500")

        self.path = tk.StringVar()
        self.results = []

        self.create_widgets()

    def create_widgets(self):
        # Selettore percorso
        path_frame = tk.Frame(self.root)
        path_frame.pack(fill='x', padx=10, pady=5)

        tk.Entry(path_frame, textvariable=self.path, width=60).pack(side='left', padx=5)
        tk.Button(path_frame, text="Sfoglia", command=self.browse_path).pack(side='left')

        # Pulsante avvio scansione
        tk.Button(self.root, text="Avvia scannerizzazione", command=self.run_scan, bg="#4CAF50", fg="white").pack(pady=10)

        # Area di testo scrollabile per i risultati
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=5)

        # Pulsante per esportare il report
        tk.Button(self.root, text="Esporta Report", command=self.export_report).pack(pady=5)

        # Pulsante per visualizzare database dei report
        tk.Button(self.root, text="Database", command=self.open_database_window).pack(pady=5)


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
        messagebox.showinfo("Report generato", f"Report salvato in {filename}")
        def open_database_window(self):
        records = recupera_report()  # List of tuples: (timestamp, report_name)

        db_win = tk.Toplevel(self.root)
        db_win.title("Storico Report")
        db_win.geometry("600x400")

        search_var = tk.StringVar()
        search_entry = tk.Entry(db_win, textvariable=search_var)
        search_entry.pack(pady=5, padx=10, fill='x')

        listbox = tk.Listbox(db_win, width=80)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def populate_list(filter_text=""):
            listbox.delete(0, tk.END)
            for ts, name in records:
                entry = f"{name} | {ts}"
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
                filename = selected.split(" | ")[0]
                full_path = os.path.join("report", "reports", filename)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    view_win = tk.Toplevel(db_win)
                    view_win.title(f"Visualizza - {filename}")
                    text_area = tk.Text(view_win, wrap=tk.WORD)
                    text_area.insert(tk.END, content)
                    text_area.config(state=tk.DISABLED)
                    text_area.pack(fill=tk.BOTH, expand=True)
                else:
                    messagebox.showerror("Errore", "File non trovato.")

        listbox.bind("<<ListboxSelect>>", show_report)


def launch_gui():
    root = tk.Tk()
    app = PrivacyWatcherGUI(root)
    root.mainloop()
