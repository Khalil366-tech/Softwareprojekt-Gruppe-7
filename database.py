# database.py
import sqlite3
from datetime import datetime
import config
from models import Artikel, Kunde, Bestellung, WarenkorbPosition

# =====================================================================
# 1. BASISEINSTELLUNGEN & INITIALISIERUNG
# =====================================================================

def get_connection():
    """Erstellt eine thread-sichere Verbindung zur SQLite-Datenbank aus config.py."""
    conn = sqlite3.connect(config.DB_PFAD)
    conn.row_factory = sqlite3.Row
    return conn


def db_initialisieren():
    """Erstellt alle benötigten Tabellen laut Lastenheft."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Kategorien
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kategorien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        # Artikel
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

        # Kunden
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

        # Bestellungen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bestellungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kundennummer TEXT NOT NULL,
                datum TEXT NOT NULL,
                gesamtbetrag REAL NOT NULL,
                FOREIGN KEY (kundennummer) REFERENCES kunden(kundennummer)
            )
        """)

        # Bestellpositionen
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
# 2. ARTIKEL-CRUD & SUCHE
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


def artikel_suchen(suchtext: str = "") -> list[Artikel]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if not suchtext:
            return alle_artikel_laden()
        query = "SELECT * FROM artikel WHERE titel LIKE ? OR kategorie LIKE ?"
        cursor.execute(query, (f"%{suchtext}%", f"%{suchtext}%"))
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
# 3. KUNDEN-CRUD
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
# 4. BESTELLUNGEN & TRANSAKTIONEN
# =====================================================================

def bestellung_speichern(kundennummer: str, gesamtbetrag: float, positionen: list[WarenkorbPosition]) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        datum_jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO bestellungen (kundennummer, datum, gesamtbetrag)
            VALUES (?, ?, ?)
        """, (kundennummer, datum_jetzt, gesamtbetrag))
        bestell_id = cursor.lastrowid

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
# 5. BERICHTE & DASHBOARD
# =====================================================================

def _formatiere_datum_fuer_sql(datum_str: str | None) -> str | None:
    if not datum_str or not datum_str.strip():
        return None
    datum_str = datum_str.strip()
    try:
        if "." in datum_str:
            teile = datum_str.split(".")
            if len(teile) == 3:
                return f"{teile[2]}-{teile[1].zfill(2)}-{teile[0].zfill(2)}"
        return datum_str
    except Exception:
        return None


def get_gesamtumsatz(start: str | None = None, ende: str | None = None) -> float:
    start_sql = _formatiere_datum_fuer_sql(start)
    ende_sql = _formatiere_datum_fuer_sql(ende)

    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT SUM(gesamtbetrag) FROM bestellungen WHERE 1=1"
        params = []
        if start_sql:
            query += " AND datum >= ?"
            params.append(f"{start_sql} 00:00:00")
        if ende_sql:
            query += " AND datum <= ?"
            params.append(f"{ende_sql} 23:59:59")
        cursor.execute(query, params)
        res = cursor.fetchone()[0]
        return float(res) if res is not None else 0.0


def get_bestellungen_anzahl(start: str | None = None, ende: str | None = None) -> int:
    start_sql = _formatiere_datum_fuer_sql(start)
    ende_sql = _formatiere_datum_fuer_sql(ende)

    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM bestellungen WHERE 1=1"
        params = []
        if start_sql:
            query += " AND datum >= ?"
            params.append(f"{start_sql} 00:00:00")
        if ende_sql:
            query += " AND datum <= ?"
            params.append(f"{ende_sql} 23:59:59")
        cursor.execute(query, params)
        res = cursor.fetchone()[0]
        return int(res) if res is not None else 0


def get_artikel_umsatzanteile(start: str | None = None, ende: str | None = None) -> list[dict]:
    start_sql = _formatiere_datum_fuer_sql(start)
    ende_sql = _formatiere_datum_fuer_sql(ende)

    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT bp.artikel_titel, SUM(bp.menge) AS gesamt_menge, SUM(bp.menge * bp.einzelpreis) AS gesamt_umsatz
            FROM bestellpositionen bp
            JOIN bestellungen b ON bp.bestell_id = b.id
            WHERE 1=1
        """
        params = []
        if start_sql:
            query += " AND b.datum >= ?"
            params.append(f"{start_sql} 00:00:00")
        if ende_sql:
            query += " AND b.datum <= ?"
            params.append(f"{ende_sql} 23:59:59")

        query += " GROUP BY bp.artikel_titel ORDER BY gesamt_umsatz DESC"
        cursor.execute(query, params)

        ergebnis = []
        for row in cursor.fetchall():
            ergebnis.append({
                "titel": row["artikel_titel"],
                "menge": row["gesamt_menge"],
                "umsatz": float(row["gesamt_umsatz"])
            })
        return ergebnis


# =====================================================================
# 6. SEEDING & BEISPIELDATEN
# =====================================================================

def beispieldaten_einfuegen():
    with get_connection() as conn:
        cursor = conn.cursor()

        for kat in config.KATEGORIEN:
            cursor.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", (kat,))

        cursor.execute("SELECT COUNT(*) FROM artikel")
        if cursor.fetchone()[0] == 0:
            test_artikel = [
                                ("HTW Saar T-Shirt Classic", "100% Bio-Baumwolle mit Frontprint", "T-Shirt", 19.99, 0.0, 15, "2026-08-01"),
                                ("HTW Saar T-Shirt Vintage", "Oversized Fit im Retro-Look", "T-Shirt", 22.50, 0.0, 10, "2026-08-02"),
                                ("WI Hoodie Classic", "Bequemer Kapuzenpullover mit Logo-Stick", "Hoodie", 39.99, 0.10, 3, "2026-08-05"),
                                ("WI Zip-Hoodie Black", "Premium Sweatjacke mit Reißverschluss", "Hoodie", 44.90, 0.0, 8, "2026-08-08"),
                                ("HTW Saar Kaffeetasse", "Keramiktasse mit Campus-Aufdruck 350ml", "Tasse", 8.50, 0.0, 20, "2026-08-10"),
                                ("Sticker-Set Campus (5er)", "Wetterfeste Vinyl-Aufkleber", "Sticker", 2.50, 0.0, 2, "2026-08-12"),
                                ("WI Thermobecher Stainless", "Hält 8h warm, auslaufsicher", "Accessoires", 14.90, 0.05, 7, "2026-08-15"),
                                ("Campus Gymbag Sportbeutel", "Robuster Turnbeutel mit Kordelzug", "Accessoires", 11.90, 0.0, 12, "2026-08-18"),
            ]

            cursor.executemany("""
                INSERT INTO artikel (titel, beschreibung, kategorie, preis, rabattsatz, lagerbestand, erstellungsdatum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, test_artikel)

        cursor.execute("SELECT COUNT(*) FROM kunden")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO kunden (kundennummer, name, strasse, plz, ort, ist_student, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("K-1001", "Max Mustermann", "Campus Alt-Saarbrücken 1", "66117", "Saarbrücken", 1, "max.mustermann@htwsaar.de"))

        conn.commit()


# =====================================================================
# 7. KOMPATIBILITÄTS-WRAPPER FÜR PERSON 5
# =====================================================================

class DatabaseManager:
    """Kompatibilitäts-Wrapper für Person 5."""
    get_gesamtumsatz = staticmethod(get_gesamtumsatz)
    get_bestellungen_anzahl = staticmethod(get_bestellungen_anzahl)
    get_artikel_umsatzanteile = staticmethod(get_artikel_umsatzanteile)
    db_initialisieren = staticmethod(db_initialisieren)
    beispieldaten_einfuegen = staticmethod(beispieldaten_einfuegen)


if __name__ == "__main__":
    db_initialisieren()
    beispieldaten_einfuegen()
    print("✅ Datenbank erfolgreich initialisiert und mit Testdaten befüllt!")