import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

import config
from backend import ShopBackend
import database
from gui_articles import ArtikelverwaltungView
from gui_customers import KundenverwaltungView
from gui_reports import ReportsWindow


class MainWindow(tk.Tk):
    """Hauptfenster der Kassenanwendung."""

    def __init__(self, db_manager=None):
        super().__init__()
        self.db = db_manager or database
        self.backend = ShopBackend(db_manager=self.db)

        self.title("WI Fanshop - Kasse & Checkout")
        self.geometry("1150x720")
        self.minsize(1000, 650)

        # Globales Styling für Tabellen
        self._konfiguriere_styles()

        # Automatische Initialisierung der Datenbank
        if hasattr(self.db, "db_initialisieren"):
            self.db.db_initialisieren()
        if hasattr(self.db, "beispieldaten_einfuegen"):
            self.db.beispieldaten_einfuegen()

        self._erstelle_layout()
        self.zeige_view("kasse")

    def _konfiguriere_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Tabellen-Design
        style.configure("Treeview", 
                        background="white", 
                        foreground="#1E293B", 
                        rowheight=26, 
                        fieldbackground="white",
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                        background="#E2E8F0", 
                        foreground="#1E293B", 
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#3B82F6")], foreground=[("selected", "white")])

    def _erstelle_layout(self):
        # 1. Sidebar links
        self.sidebar = tk.Frame(self, bg="#0F172A", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Header in der Sidebar (kompakt ohne Abschneiden)
        header_frame = tk.Frame(self.sidebar, bg="#0F172A")
        header_frame.pack(fill=tk.X, padx=10, pady=(20, 15))

        tk.Label(
            header_frame,
            text="WI FANSHOP",
            fg="white",
            bg="#0F172A",
            font=("Segoe UI", 14, "bold")
        ).pack()

        tk.Label(
            header_frame,
            text="Kasse & Verwaltung",
            fg="#94A3B8",
            bg="#0F172A",
            font=("Segoe UI", 8)
        ).pack(pady=(2, 0))

        # Navigationsbuttons
        self._nav_btn("🛒 Kasse / Checkout", lambda: self.zeige_view("kasse"))
        self._nav_btn("⚙️ Artikelverwaltung", lambda: self.zeige_view("artikel"))
        self._nav_btn("👥 Kundenverwaltung", lambda: self.zeige_view("kunden"))
        self._nav_btn("📊 Berichte / Dashboard", lambda: self.zeige_view("berichte"))

        # 2. Inhaltsbereich rechts
        self.content_area = tk.Frame(self, bg="#F8FAFC")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _nav_btn(self, text, command):
        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg="#1E293B",
            fg="#F8FAFC",
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            anchor="w",
            padx=15,
            pady=10,
            cursor="hand2",
            activebackground="#334155",
            activeforeground="white"
        )
        btn.pack(fill=tk.X, padx=10, pady=4)

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


class KassenView(tk.Frame):
    """Kassen- und Checkout-Ansicht mit Bild- und Detailvorschau."""

    def __init__(self, parent, backend: ShopBackend, db):
        super().__init__(parent, bg="#F8FAFC")
        self.backend = backend
        self.db = db
        self.aktuell_gewaehlter_artikel = None
        self.bild_referenz = None

        self._erstelle_ui()
        self._lade_kunden()
        self._lade_artikel()
        self._aktualisiere_warenkorb_view()

    def _erstelle_ui(self):
        # Links: Produktkatalog & Detail/Bild | Rechts: Warenkorb & Checkout
        self.left_frame = tk.Frame(self, bg="#F8FAFC", padx=15, pady=15)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self, bg="white", width=420, padx=15, pady=15, relief=tk.RIDGE, bd=1)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_frame.pack_propagate(False)

        self._baue_katalog_bereich()
        self._baue_checkout_bereich()

    # --- Linke Spalte ---
    # --- Linke Spalte ---
    def _baue_katalog_bereich(self):
        filter_bar = tk.Frame(self.left_frame, bg="#F8FAFC")
        filter_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_bar, text="Artikelsuche:", bg="#F8FAFC", font=("Segoe UI", 10, "bold"), fg="#1E293B").pack(side=tk.LEFT)
        self.such_entry = tk.Entry(filter_bar, width=20, font=("Segoe UI", 10))
        self.such_entry.pack(side=tk.LEFT, padx=5)

        suchen_btn = tk.Button(filter_bar, text="🔍 Suchen", command=self._artikel_filtern, bg="#334155", fg="white", font=("Segoe UI", 9), relief=tk.FLAT, padx=8, cursor="hand2")
        suchen_btn.pack(side=tk.LEFT, padx=3)

        reset_btn = tk.Button(filter_bar, text="Alle", command=lambda: self._lade_artikel(), bg="#E2E8F0", font=("Segoe UI", 9), relief=tk.FLAT, padx=8, cursor="hand2")
        reset_btn.pack(side=tk.LEFT, padx=3)

        columns = ("id", "titel", "kategorie", "preis", "bestand")
        self.artikel_tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", height=7)
        self.artikel_tree.heading("id", text="ID")
        self.artikel_tree.heading("titel", text="Titel")
        self.artikel_tree.heading("kategorie", text="Kategorie")
        self.artikel_tree.heading("preis", text="Preis (€)")
        self.artikel_tree.heading("bestand", text="Bestand")

        self.artikel_tree.column("id", width=40, anchor="center")
        self.artikel_tree.column("titel", width=220)
        self.artikel_tree.column("kategorie", width=100)
        self.artikel_tree.column("preis", width=80, anchor="e")
        self.artikel_tree.column("bestand", width=70, anchor="center")
        self.artikel_tree.pack(fill=tk.X)

        self.artikel_tree.bind("<<TreeviewSelect>>", self._on_artikel_ausgewaehlt)

        # Detailkarte
        self.preview_card = tk.Frame(self.left_frame, bg="white", highlightbackground="#CBD5E1", highlightthickness=1, padx=20, pady=20)
        self.preview_card.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.bild_container = tk.Frame(self.preview_card, bg="#F8FAFC", width=220, height=220, highlightbackground="#E2E8F0", highlightthickness=1)
        self.bild_container.pack(side=tk.LEFT, anchor="n", padx=(0, 25))
        self.bild_container.pack_propagate(False)

        self.lbl_bild = tk.Label(self.bild_container, text="📦", font=("Segoe UI Emoji", 48), bg="#F8FAFC")
        self.lbl_bild.place(relx=0.5, rely=0.5, anchor="center")

        right_detail = tk.Frame(self.preview_card, bg="white")
        right_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor="n")

        self.lbl_preview_kategorie = tk.Label(right_detail, text="", font=("Segoe UI", 9, "bold"), fg="#64748B", bg="white")
        self.lbl_preview_kategorie.pack(anchor="w")

        self.lbl_preview_titel = tk.Label(right_detail, text="Wähle einen Artikel aus", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="white")
        self.lbl_preview_titel.pack(anchor="w", pady=(2, 8))

        self.lbl_preview_desc = tk.Label(right_detail, text="Klicke auf eine Zeile oben, um Details anzuzeigen.", font=("Segoe UI", 10), fg="#475569", bg="white", wraplength=380, justify="left")
        self.lbl_preview_desc.pack(anchor="w", pady=(0, 10))

        self.lbl_preview_bestand = tk.Label(right_detail, text="", font=("Segoe UI", 10, "bold"), bg="white")
        self.lbl_preview_bestand.pack(anchor="w", pady=(0, 15))

        # Kauf-Leiste (Menge + Größe + Button)
        action_bar = tk.Frame(right_detail, bg="white")
        action_bar.pack(anchor="w")

        tk.Label(action_bar, text="Menge:", bg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.menge_spin = tk.Spinbox(action_bar, from_=1, to=100, width=3, font=("Segoe UI", 11))
        self.menge_spin.pack(side=tk.LEFT, padx=(4, 12))

        self.lbl_groesse = tk.Label(action_bar, text="Größe:", bg="white", font=("Segoe UI", 10))
        self.lbl_groesse.pack(side=tk.LEFT)
        self.groesse_cb = ttk.Combobox(action_bar, values=["S", "M", "L", "XL"], width=4, state="readonly", font=("Segoe UI", 10))
        self.groesse_cb.set("M")
        self.groesse_cb.pack(side=tk.LEFT, padx=(4, 15))

        self.add_btn = tk.Button(
            action_bar,
            text="➕ In den Warenkorb",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._artikel_zu_warenkorb
        )
        self.add_btn.pack(side=tk.LEFT)

    # --- Rechte Spalte ---
    def _baue_checkout_bereich(self):
        tk.Label(self.right_frame, text="Kunde auswählen:", bg="white", font=("Segoe UI", 10, "bold"), fg="#1E293B").pack(anchor="w")
        self.kunden_combobox = ttk.Combobox(self.right_frame, state="readonly", font=("Segoe UI", 9))
        self.kunden_combobox.pack(fill=tk.X, pady=(4, 15))
        self.kunden_combobox.bind("<<ComboboxSelected>>", self._kunde_gewaehlt)

        tk.Label(self.right_frame, text="Aktueller Warenkorb:", bg="white", font=("Segoe UI", 10, "bold"), fg="#1E293B").pack(anchor="w")

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
            bg="#EF4444",
            fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            padx=8,
            pady=3,
            cursor="hand2"
        )
        del_btn.pack(anchor="w", pady=(2, 10))

        self.lbl_zwischensumme = tk.Label(self.right_frame, text="Zwischensumme: 0.00 €", bg="white", font=("Segoe UI", 9), anchor="e")
        self.lbl_zwischensumme.pack(fill=tk.X, pady=1)

        self.lbl_rabatt = tk.Label(self.right_frame, text="Rabatt: 0.00 €", bg="white", fg="#DC2626", font=("Segoe UI", 9), anchor="e")
        self.lbl_rabatt.pack(fill=tk.X, pady=1)

        self.lbl_gesamt = tk.Label(self.right_frame, text="Gesamtsumme: 0.00 €", bg="white", font=("Segoe UI", 13, "bold"), fg="#0F172A", anchor="e")
        self.lbl_gesamt.pack(fill=tk.X, pady=(5, 15))

        order_btn = tk.Button(
            self.right_frame,
            text="💳 Jetzt Bestellen",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            pady=10,
            cursor="hand2",
            command=self._bestellung_ausfuehren
        )
        order_btn.pack(fill=tk.X)

    # --- Datenladen & Aktionen ---
    def _lade_kunden(self):
        kunden = self.db.alle_kunden_laden() if hasattr(self.db, "alle_kunden_laden") else []
        self.kunden_liste = {f"{k.name} ({getattr(k, 'kundennummer', '')})": k for k in kunden}
        self.kunden_combobox["values"] = ["Gastbestellung"] + list(self.kunden_liste.keys())
        self.kunden_combobox.current(0)

    def _lade_artikel(self, artikel_liste=None):
        for item in self.artikel_tree.get_children():
            self.artikel_tree.delete(item)

        artikeln = artikel_liste if artikel_liste is not None else self.db.alle_artikel_laden()
        for art in artikeln:
            self.artikel_tree.insert("", tk.END, values=(
                art.id, art.titel, art.kategorie, f"{art.preis:.2f}", art.lagerbestand
            ))

        # Beim Start automatisch den ersten Artikel selektieren und Bild laden
        children = self.artikel_tree.get_children()
        if children:
            self.artikel_tree.selection_set(children[0])
            self.artikel_tree.focus(children[0])
            self._on_artikel_ausgewaehlt()

    def _finde_bildpfad(self, artikel):
        """Findet Bilder vollautomatisch – ignoriert Schreibweise, Bindestriche und Unterstriche."""
        basis_ordner = os.path.join(os.path.dirname(__file__), "assets") if "__file__" in globals() else "assets"
        if not os.path.exists(basis_ordner):
            return None

        # Hilfsfunktion: Bereinigt Text von allen Trenn- und Sonderzeichen
        def bereinige(text):
            return text.lower().replace(" ", "").replace("_", "").replace("-", "").replace("(", "").replace(")", "")

        artikel_bereinigt = bereinige(artikel.titel)

        try:
            dateien_im_ordner = os.listdir(basis_ordner)
        except Exception:
            return None

        # 1. Exakter Normalisierungs-Treffer
        for datei in dateien_im_ordner:
            if not datei.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            
            dateiname_ohne_endung = os.path.splitext(datei)[0]
            datei_bereinigt = bereinige(dateiname_ohne_endung)

            # Match, wenn bereinigter Name übereinstimmt oder komplett im Namen enthalten ist
            if artikel_bereinigt == datei_bereinigt or artikel_bereinigt in datei_bereinigt or datei_bereinigt in artikel_bereinigt:
                return os.path.join(basis_ordner, datei)

        # 2. Fallback: Suche nach Schlüsselwörtern im Titel (z. B. 'kaffeetasse', 'hoodie', 'gymbag')
        schlagworte = ["tasse", "hoodie", "tshirt", "sticker", "thermobecher", "gymbag", "vintage"]
        for wort in schlagworte:
            if wort in artikel_bereinigt:
                for datei in dateien_im_ordner:
                    if wort in bereinige(datei):
                        return os.path.join(basis_ordner, datei)

        return None

    def _on_artikel_ausgewaehlt(self, event=None):
        selektiert = self.artikel_tree.selection()
        if not selektiert:
            return

        artikel_id = int(self.artikel_tree.item(selektiert[0])["values"][0])
        artikel = self.db.artikel_nach_id_laden(artikel_id) if hasattr(self.db, "artikel_nach_id_laden") else None

        if not artikel:
            return

        self.aktuell_gewaehlter_artikel = artikel
        self.lbl_preview_kategorie.config(text=artikel.kategorie.upper())
        self.lbl_preview_titel.config(text=f"{artikel.titel} — {artikel.effektiver_preis:.2f} €")
        self.lbl_preview_desc.config(text=artikel.beschreibung if artikel.beschreibung else "Keine Beschreibung vorhanden.")

        # Größen-Auswahl nur bei Kleidung aktivieren
        if artikel.kategorie in ["T-Shirt", "Hoodie"]:
            self.groesse_cb.config(state="readonly")
            if not self.groesse_cb.get():
                self.groesse_cb.set("M")
        else:
            self.groesse_cb.set("-")
            self.groesse_cb.config(state="disabled")

        if artikel.lagerbestand <= getattr(config, "FOMO_SCHWELLE", 2):
            self.lbl_preview_bestand.config(text=f"⚠️ Nur noch {artikel.lagerbestand} Stück auf Lager!", fg="#DC2626")
        else:
            self.lbl_preview_bestand.config(text=f"✓ Auf Lager: {artikel.lagerbestand} Stück", fg="#16A34A")

        bild_pfad = self._finde_bildpfad(artikel)
        if bild_pfad:
            try:
                pil_img = Image.open(bild_pfad)
                pil_img.thumbnail((220, 220), Image.Resampling.LANCZOS)
                self.bild_referenz = ImageTk.PhotoImage(pil_img)
                self.lbl_bild.config(image=self.bild_referenz, text="", bg="#F8FAFC")
            except Exception:
                self.lbl_bild.config(image="", text="📦", font=("Segoe UI Emoji", 48), bg="#F8FAFC")
        else:
            self.lbl_bild.config(image="", text="📦", font=("Segoe UI Emoji", 48), bg="#F8FAFC")

    def _artikel_filtern(self):
        text = self.such_entry.get().strip()
        gefiltert = self.db.artikel_suchen(text) if hasattr(self.db, "artikel_suchen") else []
        self._lade_artikel(gefiltert)

    def _kunde_gewaehlt(self, event=None):
        auswahl = self.kunden_combobox.get()
        kunde = self.kunden_liste.get(auswahl, None)
        self.backend.set_kunde(kunde)
        self._aktualisiere_preise()

    def _artikel_zu_warenkorb(self):
        if not self.aktuell_gewaehlter_artikel:
            selektiert = self.artikel_tree.selection()
            if not selektiert:
                messagebox.showwarning("Hinweis", "Bitte wählen Sie zuerst einen Artikel aus.")
                return
            artikel_id = int(self.artikel_tree.item(selektiert[0])["values"][0])
            self.aktuell_gewaehlter_artikel = self.db.artikel_nach_id_laden(artikel_id)

        try:
            menge = int(self.menge_spin.get())
            groesse = self.groesse_cb.get() if self.aktuell_gewaehlter_artikel.kategorie in ["T-Shirt", "Hoodie"] else None
            self.backend.artikel_hinzufuegen(self.aktuell_gewaehlter_artikel, menge, groesse=groesse)
            self._aktualisiere_warenkorb_view()
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
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
            preis = pos.positions_gesamtpreis() if hasattr(pos, "positions_gesamtpreis") else pos.artikel.preis * pos.menge
            self.cart_tree.insert("", tk.END, values=(
                pos.artikel.id, pos.artikel.titel, pos.menge, f"{preis:.2f} €"
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
    app = MainWindow(database)
    app.mainloop()