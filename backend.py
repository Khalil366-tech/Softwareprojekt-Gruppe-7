"""
backend.py - Geschäftslogik und Kassiervorgang für den WI-Fanshop.
Verantwortlich: Person 2 (/F11/ - /F14/)
"""

from datetime import datetime
import config
import database
from models import Artikel, Kunde, Warenkorb, WarenkorbPosition


class ShopBackend:
    """Verwaltet die Geschäftslogik, den Warenkorb und den Kassiervorgang."""

    def __init__(self, db_manager=None) -> None:
        self.warenkorb = Warenkorb()
        self.kunde: Kunde | None = None
        self.db = db_manager or database

    def set_kunde(self, kunde: Kunde | None) -> None:
        """Setzt den aktiven Kunden für Rabattberechnungen."""
        self.kunde = kunde

    def artikel_hinzufuegen(self, artikel: Artikel, menge: int = 1, groesse: str | None = None) -> None:
        """/F11/: Fügt einen Artikel zum Warenkorb hinzu mit Bestandsprüfung."""
        if menge <= 0:
            raise ValueError("Die Menge muss mindestens 1 betragen.")

        # Aktuell bereits im Warenkorb befindliche Menge ermitteln
        bereits_im_warenkorb = 0
        for pos in self.warenkorb.positionen:
            if pos.artikel.id == artikel.id and getattr(pos, "groesse", None) == groesse:
                bereits_im_warenkorb += pos.menge

        neue_gesamtmenge = bereits_im_warenkorb + menge

        # Lagerbestandsprüfung
        if neue_gesamtmenge > artikel.lagerbestand:
            raise ValueError(
                f"Nicht genügend Bestand für '{artikel.titel}'. "
                f"Verfügbar: {artikel.lagerbestand}, Im Warenkorb gewünscht: {neue_gesamtmenge}."
            )

        # Bestehende Position erhöhen
        for pos in self.warenkorb.positionen:
            if pos.artikel.id == artikel.id and getattr(pos, "groesse", None) == groesse:
                pos.menge += menge
                return

        # Neue Position anlegen
        neue_pos = WarenkorbPosition(artikel=artikel, menge=menge)
        setattr(neue_pos, "groesse", groesse)
        self.warenkorb.positionen.append(neue_pos)

    def artikel_entfernen(self, artikel_id: int, groesse: str | None = None) -> None:
        """/F12/: Entfernt eine Position komplett aus dem Warenkorb."""
        self.warenkorb.positionen = [
            pos for pos in self.warenkorb.positionen
            if not (pos.artikel.id == artikel_id and getattr(pos, "groesse", None) == groesse)
        ]

    def menge_aendern(self, artikel_id: int, neue_menge: int, groesse: str | None = None) -> None:
        """/F12/: Ändert die Menge einer bestehenden Position."""
        if neue_menge <= 0:
            self.artikel_entfernen(artikel_id, groesse)
            return

        for pos in self.warenkorb.positionen:
            if pos.artikel.id == artikel_id and getattr(pos, "groesse", None) == groesse:
                if neue_menge > pos.artikel.lagerbestand:
                    raise ValueError(f"Bestand nicht ausreichend. Maximal verfügbar: {pos.artikel.lagerbestand}.")
                pos.menge = neue_menge
                return

    def zwischensumme_berechnen(self) -> float:
        """/F13/: Berechnet die Zwischensumme aller Positionen (inkl. Artikelrabatten)."""
        summe = 0.0
        for pos in self.warenkorb.positionen:
            if hasattr(pos, "positions_gesamtpreis") and callable(pos.positions_gesamtpreis):
                summe += pos.positions_gesamtpreis()
            elif hasattr(pos, "gesamtpreis") and callable(pos.gesamtpreis):
                summe += pos.gesamtpreis()
            else:
                rabatt = getattr(pos.artikel, "rabattsatz", 0.0)
                einzelpreis = pos.artikel.preis * (1.0 - rabatt)
                summe += einzelpreis * pos.menge
        return round(summe, 2)

    def rabatt_berechnen(self) -> float:
        """/F13/: Berechnet Kundenrabatte (Studentenrabatt & Erstbesteller)."""
        zwischensumme = self.zwischensumme_berechnen()
        gesamtrabatt_faktor = 0.0

        if self.kunde:
            # 1. Studentenrabatt
            if getattr(self.kunde, "ist_student", False):
                gesamtrabatt_faktor += getattr(config, "STUDENTEN_RABATT_SATZ", 0.10)

            # 2. Erstbesteller-Rabatt
            if not getattr(self.kunde, "hat_erstbestellung", False) and getattr(config, "ERSTBESTELLER_RABATT_SATZ", 0.0) > 0:
                gesamtrabatt_faktor += getattr(config, "ERSTBESTELLER_RABATT_SATZ", 0.05)

        return round(zwischensumme * gesamtrabatt_faktor, 2)

    def endsumme_berechnen(self) -> float:
        """/F13/: Berechnet den finalen Zahlbetrag."""
        endsumme = self.zwischensumme_berechnen() - self.rabatt_berechnen()
        return max(0.0, round(endsumme, 2))

    def rechnung_erstellen(self, dateipfad: str | None = None) -> str:
        """Formatiert den Rechnungstext mit MwSt-Aufschlüsselung und speichert ihn in rechnung.txt."""
        pfad = dateipfad or getattr(config, "RECHNUNG_PFAD", "rechnung.txt")
        jetzt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        kunden_info = "Gastkunde (Keine Kundendaten hinterlegt)"
        if self.kunde:
            kunden_info = (
                f"Kundennr.: {getattr(self.kunde, 'kundennummer', 'N/A')}\n"
                f"Name:      {self.kunde.name}\n"
                f"Adresse:   {self.kunde.strasse}, {self.kunde.plz} {self.kunde.ort}"
            )

        trenner = "=" * 50
        zeilen = [
            trenner,
            "              WI FANSHOP - RECHNUNG              ",
            trenner,
            f"Datum: {jetzt}",
            trenner,
            "KUNDENINFORMATION:",
            kunden_info,
            trenner,
            f"{'Menge':<6}{'Artikel':<24}{'Größe':<8}{'Gesamt':>10}",
            "-" * 50,
        ]

        for pos in self.warenkorb.positionen:
            titel = pos.artikel.titel[:22]
            groesse = getattr(pos, "groesse", "-") or "-"
            pos_preis = pos.positions_gesamtpreis() if hasattr(pos, "positions_gesamtpreis") else pos.artikel.preis * pos.menge
            zeilen.append(f"{pos.menge:<6}{titel:<24}{groesse:<8}{pos_preis:>9.2f} €")

        gesamt = self.endsumme_berechnen()
        netto = round(gesamt / 1.19, 2)
        mwst = round(gesamt - netto, 2)

        zeilen.extend([
            "-" * 50,
            f"Zwischensumme:        {self.zwischensumme_berechnen():>24.2f} €",
            f"Rabatt:               {-self.rabatt_berechnen():>24.2f} €",
            trenner,
            f"GESAMTSUMME:          {gesamt:>24.2f} €",
            trenner,
            "Enthaltene Steuern:",
            f"  Netto-Warenwert:    {netto:>24.2f} €",
            f"  19% MwSt.:          {mwst:>24.2f} €",
            trenner,
            "       Vielen Dank für Ihren Einkauf!            ",
            trenner,
        ])

        rechnung_text = "\n".join(zeilen)
        with open(pfad, "w", encoding="utf-8") as f:
            f.write(rechnung_text)

        return rechnung_text

    def bestellen(self, db_manager=None) -> bool:
        """
        /F14/: Führt die Bestellung aus, speichert sie in der DB,
        schreibt die Rechnung und leert den Warenkorb.
        """
        if not self.warenkorb.positionen:
            raise ValueError("Der Warenkorb ist leer.")

        db = db_manager or self.db or database
        gesamtbetrag = self.endsumme_berechnen()
        kundennummer = self.kunde.kundennummer if self.kunde else "GAST"

        # 1. Transaktion in DB ausführen
        db.bestellung_speichern(kundennummer, gesamtbetrag, self.warenkorb.positionen)

        # 2. Rechnungsdatei generieren
        self.rechnung_erstellen()

        # 3. Warenkorb leeren
        if hasattr(self.warenkorb, "leeren"):
            self.warenkorb.leeren()
        else:
            self.warenkorb.positionen = []
        return True


if __name__ == "__main__":
    print("--- Starte Backend-Test ---")
    database.db_initialisieren()
    database.beispieldaten_einfuegen()

    shop = ShopBackend()
    kunden = database.alle_kunden_laden()
    artikel = database.alle_artikel_laden()

    print(f"Gefundene Kunden: {len(kunden)}")
    print(f"Gefundene Artikel: {len(artikel)}")

    if kunden:
        shop.set_kunde(kunden[0])
        print(f"Aktiver Kunde: {kunden[0].name}")

    if artikel:
        shop.artikel_hinzufuegen(artikel[0], menge=2)
        print(f"Artikel hinzugefügt: {artikel[0].titel}")

    print(f"Zwischensumme: {shop.zwischensumme_berechnen():.2f} €")
    print(f"Rabatt:        {shop.rabatt_berechnen():.2f} €")
    print(f"Endsumme:      {shop.endsumme_berechnen():.2f} €")

    if artikel:
        shop.bestellen()
        print("✅ Test-Bestellung erfolgreich verbucht und rechnung.txt erzeugt!")