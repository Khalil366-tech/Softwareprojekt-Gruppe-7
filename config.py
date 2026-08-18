# =====================================================================
# WI Fanshop - Zentrale Konfigurationsdatei (config.py)
# Modul: WINF-B23-440 | Hochschule: htw saar
# Single Source of Truth für alle Schwellenwerte, Pfade und Marketing-Regeln
# =====================================================================

# 1. Datenbank-Konfiguration
DB_PFAD = "fanshop.db"

# 2. htw saar Domain-Gating & Akquisitions-Marketing
# Jeder mit einer offiziellen htw saar E-Mail-Adresse (Studenten, Profs, Admin) 
# erhält automatisch den exklusiven Willkommensbonus.
UNI_DOMAIN = "@htwsaar.de"
ERSTBESTELLUNG_RABATT_SATZ = 0.20  # 20% Rabatt auf die allererste Bestellung

# 3. Allgemeine Rabatte
STANDARD_STUDENTENRABATT_SATZ = 0.10  # 10% regulärer Studentenrabatt für Folgebestellungen

# 4. Psychologische Marketing-Schwellenwerte (FOMO & Low Stock)
NIEDRIGER_BESTAND_SCHWELLE = 10        # Schwellenwert für rote Warnung in der Artikelverwaltung
FOMO_SCHWELLE = 2                     # Schwellenwert für "⚠️ Letzte Stück!" in der Kassenansicht

# 5. Cross-Selling & Bundle-Deals (Upselling-Pakete)
BUNDLE_NAME = "Freshman Starter Kit"
BUNDLE_PREIS = 45.00
