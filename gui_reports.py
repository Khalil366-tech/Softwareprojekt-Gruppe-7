# gui_reports.py - Admin-Dashboard und Berichte (Person 5)
import tkinter as tk
from tkinter import ttk
import database


class ReportsWindow(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#F8FAFC")
        self.db = db

        # Titel
        tk.Label(
            self, 
            text="📊 Admin-Dashboard & Berichte", 
            font=("Segoe UI", 16, "bold"), 
            fg="#0F172A",
            bg="#F8FAFC"
        ).pack(pady=(15, 10))

        # --- KPI-Kacheln ---
        self.kpi_frame = tk.Frame(self, bg="#F8FAFC")
        self.kpi_frame.pack(pady=10, fill="x", padx=20)

        self.kachel_umsatz = self._erstelle_kpi_kachel(self.kpi_frame, "Gesamtumsatz", "0.00 €", "#2563EB")
        self.kachel_bestellungen = self._erstelle_kpi_kachel(self.kpi_frame, "Bestellungen", "0", "#16A34A")
        self.kachel_bestseller = self._erstelle_kpi_kachel(self.kpi_frame, "Top Bestseller", "-", "#D97706")

        # --- Zeitraum-Filter (Card Look) ---
        self.zeitraum_frame = tk.Frame(self, bg="white", highlightbackground="#CBD5E1", highlightthickness=1, padx=15, pady=10)
        self.zeitraum_frame.pack(pady=15, fill="x", padx=20)

        tk.Label(self.zeitraum_frame, text="Filterzeitraum:", font=("Segoe UI", 9, "bold"), bg="white", fg="#1E293B").pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(self.zeitraum_frame, text="Von (TT.MM.JJJJ):", font=("Segoe UI", 9), bg="white", fg="#475569").pack(side=tk.LEFT, padx=5)
        self.start_entry = tk.Entry(self.zeitraum_frame, width=12, font=("Segoe UI", 9))
        self.start_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.zeitraum_frame, text="Bis:", font=("Segoe UI", 9), bg="white", fg="#475569").pack(side=tk.LEFT, padx=(15, 5))
        self.ende_entry = tk.Entry(self.zeitraum_frame, width=12, font=("Segoe UI", 9))
        self.ende_entry.pack(side=tk.LEFT, padx=5)

        self.aktualisieren_btn = tk.Button(
            self.zeitraum_frame, 
            text="🔄 Aktualisieren", 
            command=self.daten_laden, 
            bg="#0F172A", 
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.aktualisieren_btn.pack(side=tk.LEFT, padx=20)

        # --- Tabelle Detailbericht ---
        self.tabelle_frame = tk.Frame(self, bg="#F8FAFC")
        self.tabelle_frame.pack(pady=10, fill="both", expand=True, padx=20)

        tk.Label(self.tabelle_frame, text="Artikel nach Umsatzanteil", font=("Segoe UI", 11, "bold"), fg="#1E293B", bg="#F8FAFC").pack(anchor="w", pady=(0, 5))

        spalten = ("artikel", "menge", "umsatz")
        self.tabelle = ttk.Treeview(self.tabelle_frame, columns=spalten, show="headings", height=8)
        self.tabelle.heading("artikel", text="Artikelname")
        self.tabelle.heading("menge", text="Verkaufte Menge")
        self.tabelle.heading("umsatz", text="Umsatzanteil (€)")

        self.tabelle.column("artikel", width=320)
        self.tabelle.column("menge", width=120, anchor="center")
        self.tabelle.column("umsatz", width=140, anchor="e")

        self.tabelle.pack(fill="both", expand=True)

        self.daten_laden()

    def _erstelle_kpi_kachel(self, parent, titel, standard_wert, akzent_farbe):
        card = tk.Frame(parent, bg="white", highlightbackground="#CBD5E1", highlightthickness=1, padx=15, pady=12)
        card.pack(side="left", padx=8, expand=True, fill="both")

        tk.Label(card, text=titel, font=("Segoe UI", 9), fg="#64748B", bg="white").pack(anchor="w")
        val_lbl = tk.Label(card, text=standard_wert, font=("Segoe UI", 14, "bold"), fg=akzent_farbe, bg="white")
        val_lbl.pack(anchor="w", pady=(4, 0))
        return val_lbl

    def daten_laden(self):
        start = self.start_entry.get()
        ende = self.ende_entry.get()
        try:
            umsatz = self.db.get_gesamtumsatz(start, ende)
            anzahl = self.db.get_bestellungen_anzahl(start, ende)
            artikel_daten = self.db.get_artikel_umsatzanteile(start, ende)

            self.kachel_umsatz.config(text=f"{umsatz:.2f} €")
            self.kachel_bestellungen.config(text=f"{anzahl}")

            if artikel_daten:
                bestseller = artikel_daten[0].get("titel", "Unbekannt")
                self.kachel_bestseller.config(text=f"{bestseller}")
            else:
                self.kachel_bestseller.config(text="-")

            for row in self.tabelle.get_children():
                self.tabelle.delete(row)

            for art in artikel_daten:
                name = art.get("titel", "")
                menge = art.get("menge", 0)
                umsatz_anteil = art.get("umsatz", 0.0)
                self.tabelle.insert("", tk.END, values=(name, menge, f"{umsatz_anteil:.2f} €"))
        except Exception as e:
            print(f"Hinweis zu den Datenbank-Methoden: {e}")


if __name__ == "__main__":
    try:
        from database import DatabaseManager
        db_instanz = DatabaseManager()
    except Exception as e:
        print(f"Konnte Datenbank nicht laden: {e}")
        db_instanz = None

    root = tk.Tk()
    root.title("Testansicht - Admin Dashboard")
    root.geometry("800x600")

    app = ReportsWindow(root, db=db_instanz)
    app.pack(fill="both", expand=True)
    root.mainloop()