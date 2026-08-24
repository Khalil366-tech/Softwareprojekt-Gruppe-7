"""
config.py

Zentrale Konfigurationsdatei der WI Fanshop Anwendung.

Alle projektweiten Konstanten werden ausschließlich hier gepflegt
(Single Source of Truth). Kein anderes Modul darf diese Werte erneut
hartkodieren - das ist Teil der Merge-Konflikt-Vermeidungsstrategie
aus dem Projekt-Blueprint.
"""

from __future__ import annotations

# --- Datenbank ------------------------------------------------------------
DB_PFAD: str = "fanshop.db"

# --- Marketing: Rabatte -----------------------------------------------------
STUDENTEN_RABATT_SATZ: float = 0.10  # 10 % Rabatt für Kunden mit ist_student=True

# --- Marketing: Lagerbestand-Schwellenwerte ---------------------------------
# <= FOMO_SCHWELLE  -> "Nur noch X übrig!"-Hinweis in der Kassenansicht (gui_main.py)
FOMO_SCHWELLE: int = 2
# < NIEDRIGER_BESTAND_SCHWELLE -> rote Warnung in der Artikelverwaltung (gui_articles.py)
NIEDRIGER_BESTAND_SCHWELLE: int = 10

# --- Marketing: Freshman Starter Kit (Bundle) -------------------------------
FRESHMAN_STARTER_KIT_NAME: str = "Freshman Starter Kit"
FRESHMAN_STARTER_KIT_ARTIKEL: list[str] = [
    "HTW Saar T-Shirt",
    "HTW Saar Tasse",
    "HTW Saar Sticker-Set",
]
FRESHMAN_STARTER_KIT_PREIS: float = 19.99  # fester Paketpreis (Einzelsumme liegt darüber)

# --- Rechnung ----------------------------------------------------------------
RECHNUNG_DATEIPFAD: str = "rechnung.txt"
# --- Kategorien (Für die Datenbank) ---
KATEGORIEN = ["T-Shirt", "Hoodie", "Tasse", "Sticker", "Accessoires"]