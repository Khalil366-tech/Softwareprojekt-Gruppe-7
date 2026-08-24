# gui_reports.py - Admin-Dashboard und Berichte (Person 5)
import tkinter as tk
from tkinter import ttk
import database


class ReportsWindow(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#ECF0F1")
        self.db = db

        self.titel_label = tk.Label(self, text="📊 Admin-Dashboard & Berichte", font=("Arial", 16, "bold"), bg="#ECF0F1")
        self.titel_label.pack(pady=10)

        # KPI-Kacheln
        self.kpi_frame = tk.Frame(self, bg="#ECF0F1")
        self.kpi_frame.pack(pady=10, fill="x")

        self.kachel_umsatz = tk.Label(self.kpi_frame, text="Gesamtumsatz:\n-", bg="white", font=("Arial", 11), width=20, height=3, relief=tk.RIDGE, bd=1)
        self.kachel_umsatz.pack(side="left", padx=10, expand=True)

        self.kachel_bestellungen = tk.Label(self.kpi_frame, text="Bestellungen:\n-", bg="white", font=("Arial", 11), width=20, height=3, relief=tk.RIDGE, bd=1)
        self.kachel_bestellungen.pack(side="left", padx=10, expand=True)

        self.kachel_bestseller = tk.Label(self.kpi_frame, text="Bestseller:\n-", bg="white", font=("Arial", 11), width=20, height=3, relief=tk.RIDGE, bd=1)
        self.kachel_bestseller.pack(side="left", padx=10, expand=True)

        # Zeitraum-Auswahl
        self.zeitraum_frame = tk.Frame(self, bg="#ECF0F1")
        self.zeitraum_frame.pack(pady=20)

        tk.Label(self.zeitraum_frame, text="Startdatum (TT.MM.JJJJ):", bg="#ECF0F1").pack(side="left", padx=5)
        self.start_entry = tk.Entry(self.zeitraum_frame, width=12)
        self.start_entry.pack(side="left", padx=5)

        tk.Label(self.zeitraum_frame, text="Enddatum:", bg="#ECF0F1").pack(side="left", padx=5)
        self.ende_entry = tk.Entry(self.zeitraum_frame, width=12)
        self.ende_entry.pack(side="left", padx=5)

        self.aktualisieren_btn = tk.Button(self.zeitraum_frame, text="Aktualisieren", command=self.daten_laden, bg="#2980B9", fg="white")
        self.aktualisieren_btn.pack(side="left", padx=15)

        # Tabelle
        self.tabelle_frame = tk.Frame(self, bg="#ECF0F1")
        self.tabelle_frame.pack(pady=10, fill="both", expand=True, padx=20)

        tk.Label(self.tabelle_frame, text="Artikel nach Umsatzanteil", font=("Arial", 12, "bold"), bg="#ECF0F1").pack(anchor="w", pady=5)

        spalten = ("artikel", "menge", "umsatz")
        self.tabelle = ttk.Treeview(self.tabelle_frame, columns=spalten, show="headings", height=8)
        self.tabelle.heading("artikel", text="Artikelname")
        self.tabelle.heading("menge", text="Verkaufte Menge")
        self.tabelle.heading("umsatz", text="Umsatzanteil (€)")

        self.tabelle.column("artikel", width=300)
        self.tabelle.column("menge", width=120, anchor="center")
        self.tabelle.column("umsatz", width=120, anchor="e")

        self.tabelle.pack(fill="both", expand=True)

        self.daten_laden()

    def daten_laden(self):
        start = self.start_entry.get()
        ende = self.ende_entry.get()
        try:
            umsatz = self.db.get_gesamtumsatz(start, ende)
            anzahl = self.db.get_bestellungen_anzahl(start, ende)
            artikel_daten = self.db.get_artikel_umsatzanteile(start, ende)

            self.kachel_umsatz.config(text=f"Gesamtumsatz:\n{umsatz:.2f} €")
            self.kachel_bestellungen.config(text=f"Bestellungen:\n{anzahl}")

            if artikel_daten:
                bestseller = artikel_daten[0].get("titel", "Unbekannt")
                self.kachel_bestseller.config(text=f"Bestseller:\n{bestseller}")
            else:
                self.kachel_bestseller.config(text="Bestseller:\n-")

            for row in self.tabelle.get_children():
                self.tabelle.delete(row)

            for art in artikel_daten:
                name = art.get("titel", "")
                menge = art.get("menge", 0)
                umsatz_anteil = art.get("umsatz", 0.0)
                self.tabelle.insert("", tk.END, values=(name, menge, f"{umsatz_anteil:.2f}"))
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