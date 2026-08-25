# gui_articles.py - Artikelverwaltung (Person 4)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import config
from models import Artikel


class ArtikelverwaltungView(tk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg="#F8FAFC")
        self.db = db_manager
        self._erstelle_ui()
        self.lade_daten()

    def _erstelle_ui(self):
        # Titel
        tk.Label(
            self, 
            text="⚙️ Artikelverwaltung & Inventar",
            font=("Segoe UI", 16, "bold"), 
            fg="#0F172A", 
            bg="#F8FAFC"
        ).pack(pady=(15, 10))

        # --- Eingabe-Formular (Card Design) ---
        form_frame = tk.LabelFrame(
            self, 
            text=" Artikel anlegen / bearbeiten ", 
            font=("Segoe UI", 10, "bold"),
            fg="#1E293B",
            bg="white", 
            padx=15, 
            pady=15,
            highlightbackground="#CBD5E1",
            highlightthickness=1
        )
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        # Zeile 0
        tk.Label(form_frame, text="Titel:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_titel = tk.Entry(form_frame, width=28, font=("Segoe UI", 10))
        self.ent_titel.grid(row=0, column=1, padx=(5, 20), pady=4, sticky="w")

        tk.Label(form_frame, text="Kategorie:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=0, column=2, sticky="w", pady=4)
        self.ent_kat = tk.Entry(form_frame, width=20, font=("Segoe UI", 10))
        self.ent_kat.grid(row=0, column=3, padx=5, pady=4, sticky="w")

        # Zeile 1
        tk.Label(form_frame, text="Preis (€):", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_preis = tk.Entry(form_frame, width=15, font=("Segoe UI", 10))
        self.ent_preis.grid(row=1, column=1, padx=5, pady=4, sticky="w")

        tk.Label(form_frame, text="Lagerbestand:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_bestand = tk.Entry(form_frame, width=10, font=("Segoe UI", 10))
        self.ent_bestand.grid(row=1, column=3, padx=5, pady=4, sticky="w")

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0), sticky="w")

        tk.Button(
            btn_frame, 
            text="💾 Artikel speichern", 
            bg="#16A34A", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.artikel_speichern
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, 
            text="🗑️ Artikel löschen", 
            bg="#EF4444", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.artikel_loeschen
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, 
            text="🧹 Felder leeren", 
            bg="#E2E8F0",
            fg="#1E293B",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.felder_leeren
        ).pack(side=tk.LEFT)

        # --- Artikel-Tabelle ---
        table_frame = tk.Frame(self, bg="#F8FAFC")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        cols = ("id", "titel", "kategorie", "preis", "bestand")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("titel", text="Titel")
        self.tree.heading("kategorie", text="Kategorie")
        self.tree.heading("preis", text="Preis (€)")
        self.tree.heading("bestand", text="Bestand")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("titel", width=300)
        self.tree.column("kategorie", width=140)
        self.tree.column("preis", width=100, anchor="e")
        self.tree.column("bestand", width=100, anchor="center")

        # FOMO Tag konfigurieren (Subtile rote Warnung)
        self.tree.tag_configure("low_stock", background="#FEE2E2", foreground="#991B1B")

        self.tree.pack(fill=tk.BOTH, expand=True)

    def lade_daten(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        artikel_liste = self.db.alle_artikel_laden()
        schwelle = getattr(config, "NIEDRIGER_BESTAND_SCHWELLE", 10)

        for art in artikel_liste:
            tag = ("low_stock",) if art.lagerbestand < schwelle else ()
            self.tree.insert("", tk.END, values=(
                art.id, art.titel, art.kategorie, f"{art.preis:.2f}", art.lagerbestand
            ), tags=tag)

    def artikel_speichern(self):
        try:
            titel = self.ent_titel.get().strip()
            kat = self.ent_kat.get().strip()
            preis = float(self.ent_preis.get())
            bestand = int(self.ent_bestand.get())
            datum = datetime.now().strftime("%Y-%m-%d")

            if not titel or not kat:
                messagebox.showwarning("Fehler", "Titel und Kategorie dürfen nicht leer sein.")
                return

            neuer_artikel = Artikel(
                id=None, titel=titel, beschreibung="", kategorie=kat,
                preis=preis, rabattsatz=0.0, lagerbestand=bestand, erstellungsdatum=datum
            )
            self.db.artikel_hinzufuegen(neuer_artikel)
            self.lade_daten()
            self.felder_leeren()
            messagebox.showinfo("Erfolg", "Artikel erfolgreich gespeichert!")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gültige Zahlen für Preis und Bestand eingeben.")

    def artikel_loeschen(self):
        selektiert = self.tree.selection()
        if not selektiert:
            messagebox.showwarning("Hinweis", "Bitte einen Artikel aus der Tabelle auswählen.")
            return

        artikel_id = int(self.tree.item(selektiert[0])["values"][0])
        self.db.artikel_loeschen(artikel_id)
        self.lade_daten()
        messagebox.showinfo("Erfolg", "Artikel wurde gelöscht.")

    def felder_leeren(self):
        self.ent_titel.delete(0, tk.END)
        self.ent_kat.delete(0, tk.END)
        self.ent_preis.delete(0, tk.END)
        self.ent_bestand.delete(0, tk.END)