# main.py - Das Hauptprogramm
import tkinter as tk
import config
from gui.views import (
    ArtikelView, WarenkorbView, KundenView,
    AdminArtikelView, BerichteView
)

class FanshopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")

        # 1. Wir teilen das Fenster: Links Menü (dunkel), Rechts Inhalt (hell)
        self.sidebar = tk.Frame(self, width=200, bg="#2C3E50")
        self.sidebar.pack(side="left", fill="y")

        self.content_area = tk.Frame(self, bg="#ECF0F1")
        self.content_area.pack(side="right", expand=True, fill="both")

        # 2. Wir legen alle 5 Seiten wie einen Stapel Spielkarten im Inhaltsbereich ab
        self.frames = {}
        for ViewClass in (ArtikelView, WarenkorbView, KundenView, AdminArtikelView, BerichteView):
            frame = ViewClass(self.content_area)
            self.frames[ViewClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=1)

        # 3. Menü-Buttons anlegen
        self._button_anlegen("🛍️ Artikel stöbern", "ArtikelView")
        self._button_anlegen("🛒 Warenkorb", "WarenkorbView")
        self._button_anlegen("👥 Kunden", "KundenView")
        self._button_anlegen("⚙️ Artikel verwalten", "AdminArtikelView")
        self._button_anlegen("📊 Berichte", "BerichteView")

        # Erste Seite beim Start anzeigen
        self.zeige_seite("ArtikelView")

    def _button_anlegen(self, text, view_name):
        btn = tk.Button(
            self.sidebar,
            text=text,
            font=config.FONT_HEADER,
            bg="#34495E",
            fg="white",
            relief="flat",
            pady=10,
            command=lambda: self.zeige_seite(view_name)
        )
        btn.pack(fill="x", padx=5, pady=4)

    def zeige_seite(self, view_name):
        # Holt die gewünschte Seite aus dem Stapel ganz nach oben
        frame = self.frames[view_name]
        frame.tkraise()

if __name__ == "__main__":
    app = FanshopApp()
    app.mainloop()