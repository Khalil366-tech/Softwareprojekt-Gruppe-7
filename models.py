<<<<<<< HEAD

=======
>>>>>>> 23ae83192230f6495947a0a4ecb7c1350018481d
# models.py
from datetime import datetime

class Kategorie:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Artikel:
    def __init__(self, id, titel, beschreibung, kategorie, preis,
                 rabattsatz=0.0, lagerbestand=0, erstellungsdatum=None, merkmale=None):
        self.id = id
        self.titel = str(titel)
        self.beschreibung = str(beschreibung or "")
        self.kategorie = str(kategorie)
        self.preis = float(preis)
        self.rabattsatz = float(rabattsatz)
        self.lagerbestand = int(lagerbestand)
        self.erstellungsdatum = erstellungsdatum or datetime.now().strftime("%Y-%m-%d")
        self.merkmale = merkmale or {}

    @property
    def effektiver_preis(self) -> float:
        """Gibt den Preis nach Abzug des artikelbezogenen Rabattsatzes zurück."""
        return round(self.preis * (1.0 - self.rabattsatz), 2)


class Kunde:
    def __init__(self, kundennummer, name, strasse, plz, ort, ist_student=False, email=""):
        self.kundennummer = str(kundennummer)
        self.name = str(name)
        self.strasse = str(strasse)
        self.plz = str(plz)
        self.ort = str(ort)
        self.ist_student = bool(ist_student)
        self.email = str(email)


class WarenkorbPosition:
    def __init__(self, artikel: Artikel, menge: int):
        self.artikel = artikel
        self.menge = int(menge)

    def positions_gesamtpreis(self) -> float:
        """Berechnet den Gesamtpreis dieser Position unter Berücksichtigung des Artikel-Rabatts."""
        return round(self.artikel.effektiver_preis * self.menge, 2)


class Warenkorb:
    def __init__(self):
        self.positionen: list[WarenkorbPosition] = []

    def position_hinzufuegen(self, artikel: Artikel, menge: int = 1):
        for pos in self.positionen:
            if pos.artikel.id == artikel.id:
                pos.menge += menge
                return
        self.positionen.append(WarenkorbPosition(artikel, menge))

    def position_entfernen(self, artikel_id: int):
        self.positionen = [pos for pos in self.positionen if pos.artikel.id != artikel_id]

    def leeren(self):
        self.positionen.clear()

    def zwischensumme(self) -> float:
        return round(sum(pos.positions_gesamtpreis() for pos in self.positionen), 2)


class Bestellung:
    def __init__(self, id, kundennummer, datum, gesamtbetrag, positionen=None):
        self.id = id
        self.kundennummer = kundennummer
        self.datum = datum
        self.gesamtbetrag = float(gesamtbetrag)
        self.positionen = positionen or []