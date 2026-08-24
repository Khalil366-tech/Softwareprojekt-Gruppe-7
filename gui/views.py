# gui/views.py
import tkinter as tk
from tkinter import ttk, messagebox
import config

class ArtikelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. Überschrift
        tk.Label(self, text="🛍️ Artikel durchstöbern", font=config.FONT_TITLE).pack(pady=10)

        # 2. Filter- & Suchleiste
        filter_frame = tk.LabelFrame(self, text="Filter & Suche", font=config.FONT_HEADER, padx=10, pady=10)
        filter_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(filter_frame, text="Suche:", font=config.FONT_REGULAR).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_suche = tk.Entry(filter_frame, font=config.FONT_REGULAR, width=18)
        self.entry_suche.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Kategorie:", font=config.FONT_REGULAR).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        kategorien_mit_alle = ["Alle"] + config.KATEGORIEN
        self.combo_kategorie = ttk.Combobox(filter_frame, values=kategorien_mit_alle, font=config.FONT_REGULAR, state="readonly", width=14)
        self.combo_kategorie.current(0)
        self.combo_kategorie.grid(row=0, column=3, padx=5, pady=5)

        self.btn_filter = tk.Button(filter_frame, text="🔍 Suchen", font=config.FONT_REGULAR, command=self.artikel_filtern)
        self.btn_filter.grid(row=0, column=4, padx=10, pady=5)

        # 3. Artikel-Tabelle
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        spalten = ("id", "titel", "kategorie", "preis", "bestand")
        self.tree = ttk.Treeview(table_frame, columns=spalten, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("titel", text="Artikelbezeichnung")
        self.tree.heading("kategorie", text="Kategorie")
        self.tree.heading("preis", text="Preis")
        self.tree.heading("bestand", text="Lagerbestand")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("titel", width=250)
        self.tree.column("kategorie", width=120)
        self.tree.column("preis", width=80, anchor="e")
        self.tree.column("bestand", width=90, anchor="center")

        # Farb-Tag für niedrigen Lagerbestand einrichten
        self.tree.tag_configure("niedriger_bestand", foreground="#C0392B", font=("Arial", 10, "bold"))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 4. Aktionsleiste
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(action_frame, text="Menge:", font=config.FONT_REGULAR).pack(side="left", padx=5)
        self.spin_menge = tk.Spinbox(action_frame, from_=1, to=99, width=5, font=config.FONT_REGULAR)
        self.spin_menge.pack(side="left", padx=5)

        self.btn_warenkorb = tk.Button(
            action_frame, 
            text="🛒 In den Warenkorb", 
            font=config.FONT_HEADER, 
            bg="#27AE60", 
            fg="white",
            command=self.in_warenkorb_legen
        )
        self.btn_warenkorb.pack(side="right", padx=5)

        # Daten laden
        self._beispieldaten_laden()

    def _beispieldaten_laden(self):
        """Testdaten mit automatischer Farbmarkierung bei niedrigem Bestand."""
        test_artikel = [
            (1, "HTW Saar T-Shirt", "T-Shirt", f"19.99 {config.WAEHRUNGSSYMBOL}", 15),
            (2, "WI Hoodie Classic", "Hoodie", f"39.99 {config.WAEHRUNGSSYMBOL}", 3),
            (3, "HTW Saar Kaffeetasse", "Tasse", f"8.50 {config.WAEHRUNGSSYMBOL}", 20),
            (4, "Sticker-Set Campus", "Sticker", f"2.50 {config.WAEHRUNGSSYMBOL}", 1),
        ]
        for artikel in test_artikel:
            art_id, titel, kat, preis, bestand = artikel
            tag = ("niedriger_bestand",) if bestand < config.NIEDRIGER_BESTAND_SCHWELLE else ()
            self.tree.insert("", "end", values=(art_id, titel, kat, preis, f"{bestand} Stk."), tags=tag)

    def artikel_filtern(self):
        suchtext = self.entry_suche.get()
        kategorie = self.combo_kategorie.get()
        messagebox.showinfo("Suche", f"Filter aktiv:\nSuche: '{suchtext}'\nKategorie: '{kategorie}'")

    def in_warenkorb_legen(self):
        auswahl = self.tree.selection()
        if not auswahl:
            messagebox.showwarning("Hinweis", "Bitte wähle zuerst einen Artikel aus der Tabelle aus.")
            return
        
        artikel_daten = self.tree.item(auswahl[0])["values"]
        menge = self.spin_menge.get()
        messagebox.showinfo("Warenkorb", f"{menge}x '{artikel_daten[1]}' zum Warenkorb hinzugefügt!")


# =====================================================================
# PLATZHALTER-VIEWS FÜR DIE TEAMKOLLEGEN (wichtig für main.py!)
# =====================================================================

class WarenkorbView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht der Warenkorb (Person 4)", font=config.FONT_TITLE).pack(pady=30)

class KundenView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht die Kundenverwaltung (Person 3)", font=config.FONT_TITLE).pack(pady=30)

class AdminArtikelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht die Artikelverwaltung (Person 2)", font=config.FONT_TITLE).pack(pady=30)

class BerichteView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entstehen die Berichte (Person 5)", font=config.FONT_TITLE).pack(pady=30)