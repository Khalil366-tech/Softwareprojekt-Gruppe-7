# gui_customers.py - Kundenverwaltung (Person 4)
import tkinter as tk
from tkinter import ttk, messagebox
import config
from models import Kunde


class KundenverwaltungView(tk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, bg="#F8FAFC")
        self.db = db_manager
        self._erstelle_ui()
        self.lade_daten()

    def _erstelle_ui(self):
        tk.Label(
            self, 
            text="👥 Kundenverwaltung", 
            font=("Segoe UI", 16, "bold"), 
            fg="#0F172A", 
            bg="#F8FAFC"
        ).pack(pady=(15, 10))

        # --- Eingabe-Formular (Card Design) ---
        form_frame = tk.LabelFrame(
            self, 
            text=" Neuen Kunden anlegen ", 
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
        tk.Label(form_frame, text="Kundennummer:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_knr = tk.Entry(form_frame, width=16, font=("Segoe UI", 10))
        self.ent_knr.grid(row=0, column=1, sticky="w", padx=(5, 20), pady=4)

        tk.Label(form_frame, text="Name:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=0, column=2, sticky="w", pady=4)
        self.ent_name = tk.Entry(form_frame, width=28, font=("Segoe UI", 10))
        self.ent_name.grid(row=0, column=3, padx=5, pady=4, sticky="w")

        # Zeile 1
        tk.Label(form_frame, text="E-Mail:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_email = tk.Entry(form_frame, width=28, font=("Segoe UI", 10))
        self.ent_email.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=4)
        self.ent_email.bind("<KeyRelease>", self.check_uni_domain)

        # Zeile 2
        tk.Label(form_frame, text="Straße:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_str = tk.Entry(form_frame, width=28, font=("Segoe UI", 10))
        self.ent_str.grid(row=2, column=1, sticky="w", padx=(5, 20), pady=4)

        tk.Label(form_frame, text="PLZ / Ort:", font=("Segoe UI", 9), bg="white", fg="#475569").grid(row=2, column=2, sticky="w", pady=4)
        plz_ort_frame = tk.Frame(form_frame, bg="white")
        plz_ort_frame.grid(row=2, column=3, sticky="w")
        self.ent_plz = tk.Entry(plz_ort_frame, width=7, font=("Segoe UI", 10))
        self.ent_plz.pack(side=tk.LEFT, padx=(0, 5))
        self.ent_ort = tk.Entry(plz_ort_frame, width=18, font=("Segoe UI", 10))
        self.ent_ort.pack(side=tk.LEFT)

        # Zeile 3
        self.var_student = tk.BooleanVar()
        self.chk_student = tk.Checkbutton(
            form_frame, 
            text="Ist Student (10% Rabatt)", 
            variable=self.var_student,
            bg="white",
            font=("Segoe UI", 9),
            activebackground="white"
        )
        self.chk_student.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Marketing Alert Label
        self.lbl_alert = tk.Label(form_frame, text="", font=("Segoe UI", 9, "bold"), bg="white")
        self.lbl_alert.grid(row=3, column=2, columnspan=2, sticky="w", pady=(8, 0))

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(15, 0), sticky="w")

        tk.Button(
            btn_frame, 
            text="💾 Kunden speichern", 
            bg="#2563EB", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.kunde_speichern
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, 
            text="🗑️ Kunden löschen", 
            bg="#EF4444", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.kunde_loeschen
        ).pack(side=tk.LEFT)

        # --- Kunden-Tabelle ---
        table_frame = tk.Frame(self, bg="#F8FAFC")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        cols = ("knr", "name", "email", "ort", "student")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree.heading("knr", text="Kunden-Nr.")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="E-Mail")
        self.tree.heading("ort", text="Ort")
        self.tree.heading("student", text="Student?")

        self.tree.column("knr", width=100, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("email", width=220)
        self.tree.column("ort", width=150)
        self.tree.column("student", width=90, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def check_uni_domain(self, event=None):
        email = self.ent_email.get().strip().lower()
        domain = getattr(config, "UNI_DOMAIN", "@htwsaar.de").lower()

        if email.endswith(domain) and len(email) > len(domain):
            self.var_student.set(True)
            self.lbl_alert.config(text="🎓 htw saar Mitglied erkannt (Rabatt aktiv)", fg="#16A34A")
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