import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from scanner.scanner import scan_file, scan_directory
from report.report_generator import generate_txt_report
import datetime

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
        filename = f"report/Report_{timestamp}.txt"
        generate_txt_report(structured, self.path.get(), filename)
        messagebox.showinfo("Report generato", f"Report salvato in {filename}")

def launch_gui():
    root = tk.Tk()
    app = PrivacyWatcherGUI(root)
    root.mainloop()
