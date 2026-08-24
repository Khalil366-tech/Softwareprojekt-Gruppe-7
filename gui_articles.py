# gui_articles.py - Artikelverwaltung (Person 4)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import config
from models import Artikel


class ArtikelverwaltungView(tk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg="#ECF0F1")
        self.db = db_manager
        self._erstelle_ui()
        self.lade_daten()

    def _erstelle_ui(self):
        # Titel
        tk.Label(self, text="⚙️ Artikelverwaltung & Inventar (Silicon Valley FOMO-System)",
                 font=("Arial", 16, "bold"), bg="#ECF0F1").pack(pady=10)

        # --- Eingabe-Formular ---
        form_frame = tk.LabelFrame(self, text="Neuen Artikel anlegen / bearbeiten", bg="#ECF0F1", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(form_frame, text="Titel:", bg="#ECF0F1").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_titel = tk.Entry(form_frame, width=25)
        self.ent_titel.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Kategorie:", bg="#ECF0F1").grid(row=0, column=2, sticky="w", pady=2, padx=(15, 0))
        self.ent_kat = tk.Entry(form_frame, width=20)
        self.ent_kat.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form_frame, text="Preis (€):", bg="#ECF0F1").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_preis = tk.Entry(form_frame, width=15)
        self.ent_preis.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_frame, text="Lagerbestand:", bg="#ECF0F1").grid(row=1, column=2, sticky="w", pady=2, padx=(15, 0))
        self.ent_bestand = tk.Entry(form_frame, width=10)
        self.ent_bestand.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#ECF0F1")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="w")

        tk.Button(btn_frame, text="💾 Artikel speichern", bg="#27AE60", fg="white", command=self.artikel_speichern).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Artikel löschen", bg="#E74C3C", fg="white", command=self.artikel_loeschen).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🧹 Felder leeren", command=self.felder_leeren).pack(side=tk.LEFT, padx=5)

        # --- Artikel-Tabelle ---
        table_frame = tk.Frame(self, bg="#ECF0F1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        cols = ("id", "titel", "kategorie", "preis", "bestand")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("titel", text="Titel")
        self.tree.heading("kategorie", text="Kategorie")
        self.tree.heading("preis", text="Preis (€)")
        self.tree.heading("bestand", text="Bestand")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("titel", width=250)
        self.tree.column("preis", width=80, anchor="e")
        self.tree.column("bestand", width=80, anchor="center")

        # FOMO Tag konfigurieren (Rote Warnung bei niedrigem Bestand)
        self.tree.tag_configure("low_stock", background="#FADBD8", foreground="#C0392B")

        self.tree.pack(fill=tk.BOTH, expand=True)

    def lade_daten(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        artikel_liste = self.db.alle_artikel_laden()
        schwelle = getattr(config, "NIEDRIGER_BESTAND_SCHWELLE", 10)

        for art in artikel_liste:
            # Marketing Logic: Rote Markierung, wenn Bestand unter der Schwelle liegt
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