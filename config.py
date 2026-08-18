"""
config.py — Zentrale Konfigurationsdatei für das WI Fanshop-Projekt.
Single Source of Truth für alle Schwellenwerte, Pfade, GUI-Styles und Marketing-Regeln.
Modul: WINF-B23-440 | Abgabe: 25.08.2026
"""

from __future__ import annotations
from pathlib import Path

# =====================================================================
# 1. DATEI- UND VERZEICHNISPFADE
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent

# Pfad zur SQLite-Datenbankdatei
DB_NAME = "fanshop.db"
DB_PFAD = str(BASE_DIR / DB_NAME)

# Pfad zur generierten Rechnungsdatei
RECHNUNG_PFAD = str(BASE_DIR / "rechnung.txt")
RECHNUNG_DATEIPFAD = RECHNUNG_PFAD  # Alias für Abwärtskompatibilität


# =====================================================================
# 2. GUI & DESIGN (Person 1)
# =====================================================================
APP_TITLE = "WI Fanshop — htw saar"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650

FONT_TITLE = ("Arial", 14, "bold")
FONT_HEADER = ("Arial", 11, "bold")
FONT_REGULAR = ("Arial", 10)

WAEHRUNGSSYMBOL = "€"
CURRENCY = "€"                      # Alias für Abwärtskompatibilität
DEZIMALSTELLEN = 2


# =====================================================================
# 3. ARTIKEL & KATEGORIEN (Person 2)
# =====================================================================
KATEGORIEN: list[str] = ["T-Shirt", "Hoodie", "Tasse", "Sticker", "Sonstiges"]
CATEGORIES = KATEGORIEN             # Alias für Abwärtskompatibilität

VERFUEGBARE_GROESSEN: list[str] = ["XS", "S", "M", "L", "XL", "XXL"]

# Lagerbestand-Warnungen
NIEDRIGER_BESTAND_SCHWELLE: int = 5  # Rote Warnung in Artikelverwaltung
FOMO_SCHWELLE: int = 2               # Kassenansicht: "⚠️ Nur noch X Stück übrig!"


# =====================================================================
# 4. GESCHÄFTSLOGIK & RABATTE (Person 3 & 4)
# =====================================================================
UNI_DOMAIN = "@htwsaar.de"

# 10 % Rabatt für Studenten (ist_student=True)
STUDENTEN_RABATT_SATZ: float = 0.10
STUDENTENRABATT = STUDENTEN_RABATT_SATZ
STANDARD_STUDENTENRABATT_SATZ = STUDENTEN_RABATT_SATZ

# Rabatt bei Erstbestellung
ERSTBESTELLER_RABATT_SATZ: float = 0.05
REGISTRIERUNGSRABATT = ERSTBESTELLER_RABATT_SATZ
ERSTBESTELLUNG_RABATT_SATZ = ERSTBESTELLER_RABATT_SATZ


# =====================================================================
# 5. MARKETING & BUNDLES (Bonus-Features)
# =====================================================================
FRESHMAN_STARTER_KIT_NAME: str = "Freshman Starter Kit"
BUNDLE_NAME = FRESHMAN_STARTER_KIT_NAME

FRESHMAN_STARTER_KIT_ARTIKEL: list[str] = [
    "HTW Saar T-Shirt",
    "HTW Saar Tasse",
    "HTW Saar Sticker-Set",
]
FRESHMAN_STARTER_KIT_PREIS: float = 19.99
BUNDLE_PREIS = FRESHMAN_STARTER_KIT_PREIS