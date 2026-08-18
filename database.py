# database.py
import sqlite3
from datetime import datetime
import config
from models import Artikel, Kunde, Bestellung, WarenkorbPosition

def get_connection():
    """Erstellt eine thread-sichere Verbindung zur SQLite-Datenbank aus config.py."""
    conn = sqlite3.connect(config.DB_PFAD)
    conn.row_factory = sqlite3.Row
    return conn


def db_initialisieren():
    """Erstellt alle benötigten Tabellen laut Lastenheft (D01, D02, F14, F31)."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Kategorien
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kategorien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        # 2. Artikel (D01)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artikel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titel TEXT NOT NULL,
                beschreibung TEXT,
                kategorie TEXT NOT NULL,
                preis REAL NOT NULL,
                rabattsatz REAL DEFAULT 0.0,
                lagerbestand INTEGER NOT NULL,
                erstellungsdatum TEXT NOT NULL
            )
        """)

        # 3. Kunden (D02)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kunden (
                kundennummer TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                strasse TEXT NOT NULL,
                plz TEXT NOT NULL,
                ort TEXT NOT NULL,
                ist_student INTEGER DEFAULT 0,
                email TEXT
            )
        """)

        # 4. Bestellungen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bestellungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kundennummer TEXT NOT NULL,
                datum TEXT NOT NULL,
                gesamtbetrag REAL NOT NULL,
                FOREIGN KEY (kundennummer) REFERENCES kunden(kundennummer)
            )
        """)

        # 5. Bestellpositionen (für historische Berichte / Person 5)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bestellpositionen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bestell_id INTEGER NOT NULL,
                artikel_id INTEGER NOT NULL,
                artikel_titel TEXT NOT NULL,
                menge INTEGER NOT NULL,
                einzelpreis REAL NOT NULL,
                FOREIGN KEY (bestell_id) REFERENCES bestellungen(id)
            )
        """)
        conn.commit()


# =====================================================================
# ARTIKEL-CRUD (D01 / Person 1, 4 & 5)
# =====================================================================

def alle_artikel_laden() -> list[Artikel]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artikel ORDER BY id ASC")
        return [
            Artikel(
                id=row["id"],
                titel=row["titel"],
                beschreibung=row["beschreibung"],
                kategorie=row["kategorie"],
                preis=row["preis"],
                rabattsatz=row["rabattsatz"],
                lagerbestand=row["lagerbestand"],
                erstellungsdatum=row["erstellungsdatum"]
            ) for row in cursor.fetchall()
        ]

def artikel_nach_id_laden(artikel_id: int) -> Artikel | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artikel WHERE id = ?", (artikel_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Artikel(
            id=row["id"],
            titel=row["titel"],
            beschreibung=row["beschreibung"],
            kategorie=row["kategorie"],
            preis=row["preis"],
            rabattsatz=row["rabattsatz"],
            lagerbestand=row["lagerbestand"],
            erstellungsdatum=row["erstellungsdatum"]
        )

def artikel_hinzufuegen(artikel: Artikel) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO artikel (titel, beschreibung, kategorie, preis, rabattsatz, lagerbestand, erstellungsdatum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (artikel.titel, artikel.beschreibung, artikel.kategorie, artikel.preis,
              artikel.rabattsatz, artikel.lagerbestand, artikel.erstellungsdatum))
        conn.commit()
        return cursor.lastrowid

def artikel_aktualisieren(artikel: Artikel):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE artikel 
            SET titel = ?, beschreibung = ?, kategorie = ?, preis = ?, rabattsatz = ?, lagerbestand = ?
            WHERE id = ?
        """, (artikel.titel, artikel.beschreibung, artikel.kategorie, artikel.preis,
              artikel.rabattsatz, artikel.lagerbestand, artikel.id))
        conn.commit()

def artikel_loeschen(artikel_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM artikel WHERE id = ?", (artikel_id,))
        conn.commit()

def lagerbestand_aktualisieren(artikel_id: int, neuer_bestand: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE artikel SET lagerbestand = ? WHERE id = ?", (neuer_bestand, artikel_id))
        conn.commit()


# =====================================================================
# KUNDEN-CRUD (D02 / Person 1, 3 & 4)
# =====================================================================

def alle_kunden_laden() -> list[Kunde]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kunden ORDER BY name ASC")
        return [
            Kunde(
                kundennummer=row["kundennummer"],
                name=row["name"],
                strasse=row["strasse"],
                plz=row["plz"],
                ort=row["ort"],
                ist_student=bool(row["ist_student"]),
                email=row["email"] or ""
            ) for row in cursor.fetchall()
        ]

def kunde_nach_nummer_laden(kundennummer: str) -> Kunde | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kunden WHERE kundennummer = ?", (kundennummer,))
        row = cursor.fetchone()
        if not row:
            return None
        return Kunde(
            kundennummer=row["kundennummer"],
            name=row["name"],
            strasse=row["strasse"],
            plz=row["plz"],
            ort=row["ort"],
            ist_student=bool(row["ist_student"]),
            email=row["email"] or ""
        )

def kunde_hinzufuegen(kunde: Kunde):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kunden (kundennummer, name, strasse, plz, ort, ist_student, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (kunde.kundennummer, kunde.name, kunde.strasse, kunde.plz, kunde.ort,
              1 if kunde.ist_student else 0, kunde.email))
        conn.commit()

def kunde_loeschen(kundennummer: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kunden WHERE kundennummer = ?", (kundennummer,))
        conn.commit()


# =====================================================================
# BESTELLUNGEN & TRANSAKTIONEN (F14 & Berichte / Person 2 & 5)
# =====================================================================

def bestellung_speichern(kundennummer: str, gesamtbetrag: float, positionen: list[WarenkorbPosition]) -> int:
    """Speichert eine Bestellung samt Positionen und bucht Lagerbestände ab."""
    with get_connection() as conn:
        cursor = conn.cursor()
        datum_jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Bestellung anlegen
        cursor.execute("""
            INSERT INTO bestellungen (kundennummer, datum, gesamtbetrag)
            VALUES (?, ?, ?)
        """, (kundennummer, datum_jetzt, gesamtbetrag))
        bestell_id = cursor.lastrowid

        # 2. Positionen anlegen und Lagerbestand reduzieren
        for pos in positionen:
            cursor.execute("""
                INSERT INTO bestellpositionen (bestell_id, artikel_id, artikel_titel, menge, einzelpreis)
                VALUES (?, ?, ?, ?, ?)
            """, (bestell_id, pos.artikel.id, pos.artikel.titel, pos.menge, pos.artikel.effektiver_preis))

            cursor.execute("""
                UPDATE artikel 
                SET lagerbestand = MAX(0, lagerbestand - ?) 
                WHERE id = ?
            """, (pos.menge, pos.artikel.id))

        conn.commit()
        return bestell_id

def alle_bestellungen_laden() -> list[Bestellung]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bestellungen ORDER BY datum DESC")
        return [
            Bestellung(
                id=row["id"],
                kundennummer=row["kundennummer"],
                datum=row["datum"],
                gesamtbetrag=row["gesamtbetrag"]
            ) for row in cursor.fetchall()
        ]


# =====================================================================
# INITIALISIERUNG & BEISPIELDATEN (Seeding)
# =====================================================================

def beispieldaten_einfuegen():
    """Füllt die Datenbank mit Kategorien, Testartikeln und Testkunden."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Kategorien aus config.py einfügen
        for kat in config.KATEGORIEN:
            cursor.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", (kat,))

        # Testartikel einfügen, falls Tabelle leer
        cursor.execute("SELECT COUNT(*) FROM artikel")
        if cursor.fetchone()[0] == 0:
            test_artikel = [
                ("HTW Saar T-Shirt", "Klassisches Baumwoll-Shirt mit Logo", "T-Shirt", 19.99, 0.0, 15, "2026-08-01"),
                ("WI Hoodie Classic", "Bequemer Kapuzenpullover", "Hoodie", 39.99, 0.10, 3, "2026-08-05"), # Niedriger Bestand (< 5)
                ("HTW Saar Kaffeetasse", "Keramiktasse mit Campus-Aufdruck", "Tasse", 8.50, 0.0, 20, "2026-08-10"),
                ("Sticker-Set Campus", "5er Set wetterfeste Sticker", "Sticker", 2.50, 0.0, 1, "2026-08-12"), # FOMO (< 2)
            ]
            cursor.executemany("""
                INSERT INTO artikel (titel, beschreibung, kategorie, preis, rabattsatz, lagerbestand, erstellungsdatum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, test_artikel)

        # Testkunde einfügen
        cursor.execute("SELECT COUNT(*) FROM kunden")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO kunden (kundennummer, name, strasse, plz, ort, ist_student, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("K-1001", "Max Mustermann", "Campus Alt-Saarbrücken 1", "66117", "Saarbrücken", 1, "max.mustermann@htwsaar.de"))

        conn.commit()


if __name__ == "__main__":
    db_initialisieren()
    beispieldaten_einfuegen()
    print("✅ Datenbank erfolgreich initialisiert und mit Testdaten befüllt!")
    
    artikel = alle_artikel_laden()
    kunden = alle_kunden_laden()
    print(f"📦 {len(artikel)} Artikel geladen.")
    print(f"👤 {len(kunden)} Kunde(n) geladen: {kunden[0].name} ({kunden[0].email})")