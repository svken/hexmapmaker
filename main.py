"""
Hex Map Editor - Legacy Main (DEPRECATED)
Verwende stattdessen app.py für die neue modulare Struktur
"""
from app import HexMapApplication

if __name__ == "__main__":
    print("DEPRECATED: main.py ist veraltet.")
    print("Verwende 'python app.py' für die neue modulare Struktur.")
    print("Starte trotzdem die Anwendung...")
    
    app = HexMapApplication()
    app.run()