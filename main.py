# main.py - Startpunkt der Anwendung
from gui_main import MainWindow
import database

if __name__ == "__main__":
    if hasattr(database, "db_initialisieren"):
        database.db_initialisieren()
    if hasattr(database, "beispieldaten_einfuegen"):
        database.beispieldaten_einfuegen()

    app = MainWindow(database)
    app.mainloop()