# gui_customers.py - Kundenverwaltung (Person 4)
import tkinter as tk
from tkinter import ttk, messagebox
import config
from models import Kunde


class KundenverwaltungView(tk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg="#ECF0F1")
        self.db = db_manager
        self._erstelle_ui()
        self.lade_daten()

    def _erstelle_ui(self):
        tk.Label(self, text="👥 Kundenverwaltung (Smart Domain-Gating)",
                 font=("Arial", 16, "bold"), bg="#ECF0F1").pack(pady=10)

        # --- Eingabe-Formular ---
        form_frame = tk.LabelFrame(self, text="Neuen Kunden anlegen", bg="#ECF0F1", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(form_frame, text="Kundennummer:", bg="#ECF0F1").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_knr = tk.Entry(form_frame, width=15)
        self.ent_knr.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_frame, text="Name:", bg="#ECF0F1").grid(row=0, column=2, sticky="w", pady=2, padx=(15, 0))
        self.ent_name = tk.Entry(form_frame, width=25)
        self.ent_name.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form_frame, text="E-Mail:", bg="#ECF0F1").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_email = tk.Entry(form_frame, width=25)
        self.ent_email.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        # Event-Binding für Smart Domain-Gating während des Tippens
        self.ent_email.bind("<KeyRelease>", self.check_uni_domain)

        # Weitere Adressfelder
        tk.Label(form_frame, text="Straße:", bg="#ECF0F1").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_str = tk.Entry(form_frame, width=25)
        self.ent_str.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_frame, text="PLZ / Ort:", bg="#ECF0F1").grid(row=2, column=2, sticky="w", pady=2, padx=(15, 0))
        plz_ort_frame = tk.Frame(form_frame, bg="#ECF0F1")
        plz_ort_frame.grid(row=2, column=3, sticky="w")
        self.ent_plz = tk.Entry(plz_ort_frame, width=7)
        self.ent_plz.pack(side=tk.LEFT, padx=(0, 5))
        self.ent_ort = tk.Entry(plz_ort_frame, width=15)
        self.ent_ort.pack(side=tk.LEFT)

        self.var_student = tk.BooleanVar()
        self.chk_student = tk.Checkbutton(form_frame, text="Ist Student (10% Rabatt)", variable=self.var_student,
                                          bg="#ECF0F1")
        self.chk_student.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        # Marketing Alert Label (wird sichtbar bei htwsaar.de)
        self.lbl_alert = tk.Label(form_frame, text="", font=("Arial", 10, "bold"), bg="#ECF0F1")
        self.lbl_alert.grid(row=3, column=2, columnspan=2, sticky="w")

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#ECF0F1")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10, sticky="w")

        tk.Button(btn_frame, text="💾 Kunden speichern", bg="#2980B9", fg="white", command=self.kunde_speichern).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Kunden löschen", bg="#E74C3C", fg="white", command=self.kunde_loeschen).pack(
            side=tk.LEFT, padx=5)

        # --- Kunden-Tabelle ---
        table_frame = tk.Frame(self, bg="#ECF0F1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        cols = ("knr", "name", "email", "ort", "student")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree.heading("knr", text="KundenNr.")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="E-Mail")
        self.tree.heading("ort", text="Ort")
        self.tree.heading("student", text="Student?")

        self.tree.column("knr", width=100, anchor="center")
        self.tree.column("student", width=80, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def check_uni_domain(self, event=None):
        """Marketing Logic: Prüft ob die E-Mail zur Uni gehört (Domain-Gating)"""
        email = self.ent_email.get().strip().lower()
        domain = getattr(config, "UNI_DOMAIN", "@htwsaar.de").lower()

        if email.endswith(domain) and len(email) > len(domain):
            self.var_student.set(True)
            self.lbl_alert.config(text="🎓 htw saar Mitglied erkannt: Willkommensrabatt aktiv!", fg="#27AE60")
        else:
            self.var_student.set(False)
            self.lbl_alert.config(text="")

    def lade_daten(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        kunden_liste = self.db.alle_kunden_laden()
        for k in kunden_liste:
            student_str = "Ja 🎓" if k.ist_student else "Nein"
            self.tree.insert("", tk.END, values=(k.kundennummer, k.name, k.email, k.ort, student_str))

    def kunde_speichern(self):
        knr = self.ent_knr.get().strip()
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        stras = self.ent_str.get().strip()
        plz = self.ent_plz.get().strip()
        ort = self.ent_ort.get().strip()
        ist_stud = self.var_student.get()

        if not knr or not name:
            messagebox.showwarning("Fehler", "Kundennummer und Name sind Pflichtfelder.")
            return

        neuer_kunde = Kunde(
            kundennummer=knr, name=name, strasse=stras,
            plz=plz, ort=ort, ist_student=ist_stud, email=email
        )
        self.db.kunde_hinzufuegen(neuer_kunde)
        self.lade_daten()
        messagebox.showinfo("Erfolg", f"Kunde {name} wurde gespeichert!")

    def kunde_loeschen(self):
        selektiert = self.tree.selection()
        if not selektiert:
            messagebox.showwarning("Hinweis", "Bitte einen Kunden auswählen.")
            return

        knr = self.tree.item(selektiert[0])["values"][0]
        self.db.kunde_loeschen(str(knr))
        self.lade_daten()
        messagebox.showinfo("Erfolg", "Kunde wurde gelöscht.")