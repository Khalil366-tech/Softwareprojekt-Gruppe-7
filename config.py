"""
config.py - Zentrale Konfigurationsdatei der WI Fanshop Anwendung.
Single Source of Truth für alle Schwellenwerte, Pfade, GUI-Styles und Marketing-Regeln.
"""

from __future__ import annotations
from pathlib import Path

# --- Pfade & Datenbank ---
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = "fanshop.db"
DB_PFAD = str(BASE_DIR / DB_NAME)

RECHNUNG_PFAD = str(BASE_DIR / "rechnung.txt")
RECHNUNG_DATEIPFAD = RECHNUNG_PFAD

# --- GUI & Layout ---
APP_TITLE = "WI Fanshop — Kassen & Checkout"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

FONT_TITLE = ("Arial", 14, "bold")
FONT_HEADER = ("Arial", 11, "bold")
FONT_REGULAR = ("Arial", 10)

WAEHRUNGSSYMBOL = "€"
CURRENCY = "€"

# --- Kategorien & Artikel ---
KATEGORIEN: list[str] = ["T-Shirt", "Hoodie", "Tasse", "Sticker", "Accessoires"]
CATEGORIES = KATEGORIEN
VERFUEGBARE_GROESSEN: list[str] = ["XS", "S", "M", "L", "XL", "XXL"]

# --- Schwellenwerte ---
NIEDRIGER_BESTAND_SCHWELLE: int = 10
FOMO_SCHWELLE: int = 2

# --- Rabatte & Marketing ---
UNI_DOMAIN = "@htwsaar.de"
STUDENTEN_RABATT_SATZ: float = 0.10
ERSTBESTELLER_RABATT_SATZ: float = 0.05

FRESHMAN_STARTER_KIT_NAME: str = "Freshman Starter Kit"
FRESHMAN_STARTER_KIT_ARTIKEL: list[str] = [
    "HTW Saar T-Shirt",
    "HTW Saar Tasse",
    "HTW Saar Sticker-Set",
]
FRESHMAN_STARTER_KIT_PREIS: float = 19.99