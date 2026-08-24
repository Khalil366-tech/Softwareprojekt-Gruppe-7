import tkinter as tk
from tkinter import ttk, messagebox
import config
from backend import ShopBackend
import database
from gui_articles import ArtikelverwaltungView
from gui_customers import KundenverwaltungView
from gui_reports import ReportsWindow


class MainWindow(tk.Tk):
    """Hauptfenster der Kassenanwendung (Person 3)."""

    def __init__(self, db_manager=None):
        super().__init__()
        self.db = db_manager or database
        self.backend = ShopBackend(db_manager=self.db)

        self.title("WI Fanshop- Kassen & Checkout")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # 1. Automatische Initialisierung der Datenbank sicherstellen
        if hasattr(self.db, "db_initialisieren"):
            self.db.db_initialisieren()
        if hasattr(self.db, "beispieldaten_einfuegen"):
            self.db.beispieldaten_einfuegen()

        self._erstelle_layout()
        self.zeige_view("kasse")

    def _erstelle_layout(self):
        # 1. Sidebar links
        self.sidebar = tk.Frame(self, bg="#2C3E50", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text=getattr(config, "APP_TITLE", "WI FANSHOP"),
            fg="white",
            bg="#2C3E50",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        # Navigationsbuttons
        self._nav_btn("🛒 Kasse / Checkout", lambda: self.zeige_view("kasse"))
        self._nav_btn("⚙️ Artikelverwaltung", lambda: self.zeige_view("artikel"))
        self._nav_btn("👥 Kundenverwaltung", lambda: self.zeige_view("kunden"))
        self._nav_btn("📊 Berichte / Dashboard", lambda: self.zeige_view("berichte"))

        # 2. Inhaltsbereich rechts
        self.content_area = tk.Frame(self, bg="#ECF0F1")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _nav_btn(self, text, command):
        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg="#34495E",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 11),
            anchor="w",
            padx=15,
            pady=10
        )
        btn.pack(fill=tk.X, padx=8, pady=4)

    def zeige_view(self, view_name: str):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        if view_name == "kasse":
            view = KassenView(self.content_area, self.backend, self.db)
            view.pack(fill=tk.BOTH, expand=True)
        elif view_name == "artikel":
            view = ArtikelverwaltungView(self.content_area, self.db)
            view.pack(fill=tk.BOTH, expand=True)
        elif view_name == "kunden":
            view = KundenverwaltungView(self.content_area, self.db)
            view.pack(fill=tk.BOTH, expand=True)
        elif view_name == "berichte":
            view = ReportsWindow(self.content_area, self.db)
            view.pack(fill=tk.BOTH, expand=True)

    def _zeige_platzhalter(self, titel):
        tk.Label(
            self.content_area,
            text=f"{titel}\n\n(Dieses Modul wird von einem Teammitglied erstellt)",
            font=("Arial", 14),
            bg="#ECF0F1",
            fg="#7F8C8D"
        ).pack(expand=True)

class KassenView(tk.Frame):
    """Kassen- und Checkout-Ansicht (Person 3)."""

    def __init__(self, parent, backend: ShopBackend, db):
        super().__init__(parent, bg="#ECF0F1")
        self.backend = backend
        self.db = db

        self._erstelle_ui()
        self._lade_kunden()
        self._lade_artikel()
        self._aktualisiere_warenkorb_view()

    def _erstelle_ui(self):
        # Links: Produktkatalog & Suche | Rechts: Warenkorb & Kasse
        self.left_frame = tk.Frame(self, bg="#ECF0F1", padx=15, pady=15)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self, bg="white", width=420, padx=15, pady=15, relief=tk.RIDGE, bd=1)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_frame.pack_propagate(False)

        self._baue_katalog_bereich()
        self._baue_checkout_bereich()

    # --- Linke Spalte ---
    def _baue_katalog_bereich(self):
        filter_bar = tk.Frame(self.left_frame, bg="#ECF0F1")
        filter_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_bar, text="Artikelsuche:", bg="#ECF0F1", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.such_entry = tk.Entry(filter_bar, width=22)
        self.such_entry.pack(side=tk.LEFT, padx=5)

        suchen_btn = tk.Button(filter_bar, text="🔍 Suchen", command=self._artikel_filtern, bg="#34495E", fg="white")
        suchen_btn.pack(side=tk.LEFT, padx=3)

        reset_btn = tk.Button(filter_bar, text="Alle", command=lambda: self._lade_artikel(), bg="#BDC3C7")
        reset_btn.pack(side=tk.LEFT, padx=3)

        columns = ("id", "titel", "kategorie", "preis", "bestand")
        self.artikel_tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", height=15)
        self.artikel_tree.heading("id", text="ID")
        self.artikel_tree.heading("titel", text="Titel")
        self.artikel_tree.heading("kategorie", text="Kategorie")
        self.artikel_tree.heading("preis", text="Preis (€)")
        self.artikel_tree.heading("bestand", text="Bestand")

        self.artikel_tree.column("id", width=40, anchor="center")
        self.artikel_tree.column("titel", width=220)
        self.artikel_tree.column("kategorie", width=110)
        self.artikel_tree.column("preis", width=80, anchor="e")
        self.artikel_tree.column("bestand", width=70, anchor="center")
        self.artikel_tree.pack(fill=tk.BOTH, expand=True)

        action_bar = tk.Frame(self.left_frame, bg="#ECF0F1")
        action_bar.pack(fill=tk.X, pady=10)

        tk.Label(action_bar, text="Menge:", bg="#ECF0F1").pack(side=tk.LEFT)
        self.menge_spin = tk.Spinbox(action_bar, from_=1, to=100, width=5)
        self.menge_spin.pack(side=tk.LEFT, padx=5)

        add_btn = tk.Button(
            action_bar,
            text="➕ In den Warenkorb",
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=4,
            command=self._artikel_zu_warenkorb
        )
        add_btn.pack(side=tk.LEFT, padx=10)

    # --- Rechte Spalte ---
    def _baue_checkout_bereich(self):
        tk.Label(self.right_frame, text="Kunde auswählen:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        self.kunden_combobox = ttk.Combobox(self.right_frame, state="readonly")
        self.kunden_combobox.pack(fill=tk.X, pady=(3, 15))
        self.kunden_combobox.bind("<<ComboboxSelected>>", self._kunde_gewaehlt)

        tk.Label(self.right_frame, text="Aktueller Warenkorb:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")

        cart_cols = ("id", "titel", "menge", "summe")
        self.cart_tree = ttk.Treeview(self.right_frame, columns=cart_cols, show="headings", height=8)
        self.cart_tree.heading("id", text="ID")
        self.cart_tree.heading("titel", text="Artikel")
        self.cart_tree.heading("menge", text="Menge")
        self.cart_tree.heading("summe", text="Gesamt")

        self.cart_tree.column("id", width=30, anchor="center")
        self.cart_tree.column("titel", width=160)
        self.cart_tree.column("menge", width=60, anchor="center")
        self.cart_tree.column("summe", width=80, anchor="e")
        self.cart_tree.pack(fill=tk.X, pady=5)

        del_btn = tk.Button(
            self.right_frame,
            text="🗑️ Position entfernen",
            command=self._position_entfernen,
            bg="#E74C3C",
            fg="white"
        )
        del_btn.pack(anchor="w", pady=(0, 10))

        self.lbl_zwischensumme = tk.Label(self.right_frame, text="Zwischensumme: 0.00 €", bg="white", anchor="e")
        self.lbl_zwischensumme.pack(fill=tk.X, pady=1)

        self.lbl_rabatt = tk.Label(self.right_frame, text="Rabatt: 0.00 €", bg="white", fg="#C0392B", anchor="e")
        self.lbl_rabatt.pack(fill=tk.X, pady=1)

        self.lbl_gesamt = tk.Label(self.right_frame, text="Gesamtsumme: 0.00 €", bg="white", font=("Arial", 12, "bold"), anchor="e")
        self.lbl_gesamt.pack(fill=tk.X, pady=(5, 15))

        order_btn = tk.Button(
            self.right_frame,
            text="💳 Jetzt Bestellen",
            bg="#2980B9",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=8,
            command=self._bestellung_ausfuehren
        )
        order_btn.pack(fill=tk.X)

    # --- Datenladen & Aktionen ---
    def _lade_kunden(self):
        if hasattr(self.db, "get_all_kunden"):
            kunden = self.db.get_all_kunden()
        elif hasattr(self.db, "alle_kunden_laden"):
            kunden = self.db.alle_kunden_laden()
        else:
            kunden = []

        self.kunden_liste = {f"{k.name} ({getattr(k, 'kundennummer', getattr(k, 'id', ''))})": k for k in kunden}
        self.kunden_combobox["values"] = ["Gastbestellung"] + list(self.kunden_liste.keys())
        self.kunden_combobox.current(0)

    def _lade_artikel(self, artikel_liste=None):
        for item in self.artikel_tree.get_children():
            self.artikel_tree.delete(item)

        if artikel_liste is not None:
            artikeln = artikel_liste
        elif hasattr(self.db, "alle_artikel_laden"):
            artikeln = self.db.alle_artikel_laden()
        elif hasattr(self.db, "get_all_artikel"):
            artikeln = self.db.get_all_artikel()
        elif hasattr(self.db, "artikel_laden"):
            artikeln = self.db.artikel_laden()
        else:
            print("⚠️ Keine passende Funktion zum Laden der Artikel in database.py gefunden!")
            artikeln = []

        print(f"📦 Geladene Artikel aus der DB: {len(artikeln)}")

        for art in artikeln:
            print(f"   -> Artikel: {getattr(art, 'titel', getattr(art, 'name', 'Unbekannt'))}")
            art_id = getattr(art, "id", getattr(art, "artikel_id", 0))
            titel = getattr(art, "titel", getattr(art, "name", "-"))
            kategorie = getattr(art, "kategorie", "-")
            preis = getattr(art, "preis", 0.0)
            bestand = getattr(art, "lagerbestand", getattr(art, "bestand", 0))

            self.artikel_tree.insert("", tk.END, values=(
                art_id, titel, kategorie, f"{preis:.2f}", bestand
            ))
    def _artikel_filtern(self):
        text = self.such_entry.get().strip()
        if hasattr(self.db, "suche_artikel"):
            gefiltert = self.db.suche_artikel(suchtext=text if text else None)
        elif hasattr(self.db, "artikel_suchen"):
            gefiltert = self.db.artikel_suchen(text)
        else:
            gefiltert = []
        self._lade_artikel(gefiltert)

    def _kunde_gewaehlt(self, event=None):
        auswahl = self.kunden_combobox.get()
        kunde = self.kunden_liste.get(auswahl, None)
        self.backend.set_kunde(kunde)
        self._aktualisiere_preise()

    def _artikel_zu_warenkorb(self):
        selektiert = self.artikel_tree.selection()
        if not selektiert:
            messagebox.showwarning("Hinweis", "Bitte wählen Sie zuerst einen Artikel aus.")
            return

        artikel_id = int(self.artikel_tree.item(selektiert[0])["values"][0])
        menge = int(self.menge_spin.get())

        if hasattr(self.db, "get_artikel_by_id"):
            artikel = self.db.get_artikel_by_id(artikel_id)
        elif hasattr(self.db, "artikel_nach_id_laden"):
            artikel = self.db.artikel_nach_id_laden(artikel_id)
        else:
            messagebox.showerror("Fehler", "Artikel konnte nicht geladen werden.")
            return

        try:
            self.backend.artikel_hinzufuegen(artikel, menge)
            self._aktualisiere_warenkorb_view()
        except ValueError as e:
            messagebox.showerror("Bestandsfehler", str(e))

    def _position_entfernen(self):
        selektiert = self.cart_tree.selection()
        if not selektiert:
            messagebox.showwarning("Hinweis", "Bitte wählen Sie eine Position aus dem Warenkorb aus.")
            return

        artikel_id = int(self.cart_tree.item(selektiert[0])["values"][0])
        self.backend.artikel_entfernen(artikel_id)
        self._aktualisiere_warenkorb_view()

    def _aktualisiere_warenkorb_view(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        for pos in self.backend.warenkorb.positionen:
            art_id = getattr(pos.artikel, "artikel_id", getattr(pos.artikel, "id", 0))
            preis = pos.positions_gesamtpreis() if hasattr(pos, "positions_gesamtpreis") else pos.artikel.preis * pos.menge
            self.cart_tree.insert("", tk.END, values=(
                art_id, pos.artikel.titel, pos.menge, f"{preis:.2f} €"
            ))

        self._aktualisiere_preise()

    def _aktualisiere_preise(self):
        zw = self.backend.zwischensumme_berechnen()
        rab = self.backend.rabatt_berechnen()
        end = self.backend.endsumme_berechnen()

        self.lbl_zwischensumme.config(text=f"Zwischensumme: {zw:.2f} €")
        self.lbl_rabatt.config(text=f"Rabatt: -{rab:.2f} €")
        self.lbl_gesamt.config(text=f"Gesamtsumme: {end:.2f} €")

    def _bestellung_ausfuehren(self):
        try:
            self.backend.bestellen()
            messagebox.showinfo("Erfolg", "Bestellung erfolgreich abgeschlossen!\nRechnung rechnung.txt wurde erstellt.")
            self._aktualisiere_warenkorb_view()
            self._lade_artikel()
        except ValueError as e:
            messagebox.showerror("Fehler beim Bestellen", str(e))
        except Exception as e:
            messagebox.showerror("Fehler", f"Bestellung konnte nicht durchgeführt werden:\n{str(e)}")


if __name__ == "__main__":
    # Datenbank sicher initialisieren
    if hasattr(database, "db_initialisieren"):
        database.db_initialisieren()
    if hasattr(database, "beispieldaten_einfuegen"):
        database.beispieldaten_einfuegen()

    app = MainWindow(database)
    app.mainloop()