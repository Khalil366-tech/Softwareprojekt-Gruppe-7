# gui/views.py - Die einzelnen Seiten/Ansichten
import tkinter as tk
import config

# Seite 1: Artikel anzeigen
class ArtikelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entstehen die Artikel (Person 2)", font=config.FONT_TITLE).pack(pady=30)

# Seite 2: Warenkorb
class WarenkorbView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht der Warenkorb (Person 4)", font=config.FONT_TITLE).pack(pady=30)

# Seite 3: Kunden
class KundenView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht die Kundenverwaltung (Person 3)", font=config.FONT_TITLE).pack(pady=30)

# Seite 4: Admin
class AdminArtikelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entsteht die Artikelverwaltung (Person 2)", font=config.FONT_TITLE).pack(pady=30)

# Seite 5: Berichte
class BerichteView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Hier entstehen die Berichte (Person 5)", font=config.FONT_TITLE).pack(pady=30)