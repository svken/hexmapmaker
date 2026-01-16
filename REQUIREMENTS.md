# Python Hex Map Editor für Idle War - Detaillierter Entwicklungsauftrag

Entwickle einen modularen Python-basierten Karteneditor für das Godot-Spiel "Idle War". Der Editor soll hexagonale Karten erstellen, bearbeiten und exportieren können.

## 🎯 Hauptziele

1. **Modular aufgebaute Anwendung** mit separaten Modulen für verschiedene Funktionen
2. **Intuitive GUI** zum Erstellen und Bearbeiten von Hex-Karten
3. **Export-Kompatibilität** mit dem bestehenden Godot-Projekt
4. **Erweiterbarkeit** für zukünftige Features

## 📊 Datenstrukturen (aus Godot-Projekt übernommen)

### TileClass Eigenschaften
```python
class Tile:
    # Grundlegende Eigenschaften
    coordinates: tuple[int, int]  # (x, y) Hex-Koordinaten
    area: AreaClass  # Terrain-Typ
    is_land: bool
    
    # Ressourcen System  
    resource: ResourceType  # STEEL, HUMANS
    resource_count: float
    resource_regeneration_rate: float = 0.1
    max_resource_capacity: float = 10.0
    
    # Militär und Kampf
    faction: FactionType  # BLUE, RED, NEUTRAL
    in_battle: bool = False
    front_degree: int = 0
    strength: float
    fortification_level: int = 0
    garrison_size: int = 0
    
    # Erweiterte Eigenschaften
    elevation: float = 0.0  # Höhe über Meeresspiegel
    temperature: float = 20.0  # Temperatur in Celsius
    fertility: float = 1.0  # Fruchtbarkeit
    accessibility: float = 1.0  # Erreichbarkeit
    
    # Strukturen
    structures: list[str] = []  # IDs der Strukturen
    population: int = 0
    happiness: float = 50.0
    
    # Strategische Information
    strategic_value: int = 1
    supply_lines: list[tuple[int, int]] = []
    visibility: int = 1
    
    # UI
    is_selected: bool = False
    neighbour_tiles: int = 0
```

### AreaClass (Terrain-Typen)
```python
class Area:
    id: str  # "desert", "plain", "mountains", "city", "water"
    display_name: str
    move_cost: int
    attack_mult: float
    defense_mult: float
```

### Verfügbare Terrain-Typen
- **Desert**: move_cost=3, attack_mult=0.8, defense_mult=0.9
- **Plain**: move_cost=3, attack_mult=0.8, defense_mult=0.9  
- **Mountains**: move_cost=4, attack_mult=10, defense_mult=20
- **City**: move_cost=2, attack_mult=0.9, defense_mult=1.4
- **Water**: move_cost=100, attack_mult=0, defense_mult=0

### GridClass
```python
class Grid:
    width: int = 100
    height: int = 100
    tiles: list[Tile] = []
    area_definitions: list[Area] = []
```

## 🏗️ Modulare Projektstruktur

### 1. **main.py** - Haupt-Anwendung
- GUI-Initialisierung mit tkinter/PyQt
- Hauptfenster-Layout
- Menüleiste (File, Edit, View, Tools, Help)
- Event-Handling zwischen Modulen

### 2. **data/models.py** - Datenmodelle
- `Tile` Klasse mit allen Attributen
- `Area` Klasse für Terrain-Definitionen  
- `Grid` Klasse für Kartendaten
- `ResourceType` und `FactionType` Enums
- Hex-Koordinaten Hilfsfunktionen

### 3. **data/grid_manager.py** - Grid-Verwaltung
- Grid-Erstellung und -Initialisierung
- Hex-Nachbarschafts-Berechnungen (odd-r offset system)
- Tile-Zugriff per Koordinaten
- Grid-Validierung

### 4. **generation/generators.py** - Prozedural-Generation
- **NoiseGenerator**: Perlin/Simplex Noise für Terrain
- **BiomeGenerator**: Biom-Zuordnung basierend auf Elevation/Moisture
- **FactionGenerator**: Faction-Grenzen mit Smoothing
- **ResourceGenerator**: Ressourcen-Verteilung
- Template-Maps (Insel, Kontinent, Archipel)

### 5. **ui/map_canvas.py** - Karten-Darstellung
- Hex-Grid Rendering mit tkinter Canvas oder PyQt
- Zoom- und Pan-Funktionalität
- Tile-Highlighting bei Hover/Selection
- Farb-Coding für Factions, Terrain, Resources
- Grid-Overlay toggle

### 6. **ui/toolbox.py** - Editor-Werkzeuge
- **Paint-Tool**: Terrain-Typen malen
- **Faction-Tool**: Faction-Zuordnung
- **Resource-Tool**: Ressourcen platzieren
- Brush-Größe Einstellung

### 7. **ui/property_panel.py** - Eigenschaften-Editor
- Tile-Eigenschaften bearbeiten (wenn ausgewählt)
- Batch-Editing für mehrere Tiles
- Sliders für numerische Werte
- Dropdowns für Enums
- Validierung der Eingaben

### 8. **ui/layer_panel.py** - Layer-Verwaltung
- Layer für: Terrain, Factions, Resources, Elevation, etc.
- Layer ein-/ausblenden
- Layer-spezifische Visualisierung
- Opacity-Kontrolle

### 9. **io/godot_exporter.py** - Godot-Export
- Export zu Godot-kompatiblen .tres Dateien
- GridClass Resource-Format
- TileClass Array-Export
- Metadata-Erhaltung

### 10. **io/file_manager.py** - Dateiverwaltung
- Projekt speichern/laden (JSON/Pickle Format)
- Import/Export verschiedener Formate
- Auto-Save Funktionalität
- Recent Files Management

### 11. **utils/hex_math.py** - Hex-Mathematik
- Hex-zu-Pixel Konvertierung
- Pixel-zu-Hex Konvertierung  
- Hex-Distanz Berechnungen
- Hex-Nachbarn Funktionen (odd-r offset)
- Hex-Linien und -Bereiche

### 12. **utils/noise.py** - Noise-Generierung
- Perlin/Simplex Noise Implementation oder Wrapper
- Multi-Octave Noise
- Noise-Kombinationen
- Seeded Random Generation

## 🎨 GUI-Layout Anforderungen

### Hauptfenster-Bereiche:
1. **Menüleiste** - Standard File/Edit/View Menüs
2. **Toolbar** - Schnellzugriff auf Tools
3. **Map Canvas** - Hauptbereich für Karten-Display (70% der Fläche)
4. **Toolbox Panel** - Werkzeuge auf der linken Seite
5. **Properties Panel** - Eigenschaften auf der rechten Seite  
6. **Layer Panel** - Layer-Kontrolle (dockbar)
7. **Status Bar** - Koordinaten, Zoom-Level, etc.

## 🔧 Kern-Funktionalitäten

### Map Generation:
- Neue Karte erstellen (Größe wählbar: 50x50 bis 200x200)
- Template auswählen (Empty, Island, Continent, Archipelago)
- Noise-basierte Generation mit Parametern
- Faction-Grenzen automatisch generieren

### Editing Tools:
- **Paint Brush**: Terrain malen mit verschiedenen Pinselgrößen
- **Fill Tool**: Zusammenhängende Bereiche füllen
- **Selection**: Rechteck/Kreis/Lasso-Auswahl
- **Faction Painter**: Faction-Zugehörigkeit ändern
- **Resource Placer**: Ressourcen-Vorkommen setzen

### Visualization Modes:
- **Terrain View**: Standard Terrain-Farben
- **Faction View**: Factions farblich hervorgehoben  
- **Resource View**: Ressourcen-Vorkommen anzeigen
- **Elevation View**: Höhen-basierte Farbgebung
- **Front Lines**: Kampf-Fronten visualisieren

### Import/Export:
- Godot .tres Format Export
- JSON Export/Import für externe Tools
- Bild-Export (PNG) für Dokumentation
- Template-Export für Wiederverwendung

## 🎮 Hex-Koordinatensystem (aus Godot übernommen)

Verwende das **"odd-r offset"** System aus dem Godot-Projekt:

```python
def get_hex_neighbors(x: int, y: int) -> list[tuple[int, int]]:
    """Hex-Nachbarn für odd-r offset System"""
    odd = (y & 1) == 1
    
    if odd:
        return [
            (x - 1, y), (x + 1, y),      # links, rechts
            (x, y - 1), (x + 1, y - 1),  # oben-links, oben-rechts  
            (x, y + 1), (x + 1, y + 1),  # unten-links, unten-rechts
        ]
    else:
        return [
            (x - 1, y), (x + 1, y),      # links, rechts
            (x - 1, y - 1), (x, y - 1),  # oben-links, oben-rechts
            (x - 1, y + 1), (x, y + 1),  # unten-links, unten-rechts  
        ]
```

## 🔌 Export-Format für Godot

Der Export sollte eine `.tres` Datei erstellen, die direkt in Godot als `GridClass` Resource geladen werden kann:

```
[gd_resource type="Resource" script_class="GridClass" load_steps=2 format=3]

[ext_resource type="Script" path="res://game/scripts/map/grid_class.gd" id="1"]

[resource]
script = ExtResource("1")
width = 100
height = 100  
tiles = [/* TileClass Array */]
area_definitions = [/* AreaClass Array */]
```

## 🛠️ Technische Anforderungen

### Dependencies:
- **tkinter** oder **PyQt6** für GUI
- **Pillow** für Image-Handling  
- **numpy** für Noise-Generation und Array-Operationen
- **noise** library für Perlin/Simplex Noise
- **json** für Serialisierung

### Performance:
- Effiziente Hex-Grid Rendering für große Karten (100x100+)
- Lazy-Loading für große Karten-Bereiche
- Responsive UI auch bei komplexen Operationen
- Undo/Redo System für Editor-Aktionen

### Code-Qualität:
- Type-Hints für alle Funktionen
- Docstrings für Module und wichtige Funktionen
- Error-Handling und Validierung
- Modular und erweiterbar
- Clean Code Prinzipien

## 📋 Implementierungs-Prioritäten

### Phase 1 - Core (MVP):
1. Datenmodelle und Grid-Verwaltung ✅
2. Basis-GUI mit Map Canvas ✅
3. Grundlegende Tools (Paint, Select)
4. Godot-Export

### Phase 2 - Tools:
1. Erweiterte Editing-Tools
2. Layer-System
3. Property-Panel
4. Undo/Redo

### Phase 3 - Generation:
1. Noise-basierte Terrain-Generation
2. Template-System
3. Faction-Generation
4. Resource-Placement

### Phase 4 - Polish:
1. Erweiterte Visualisierung
2. Performance-Optimierungen
3. Zusätzliche Export-Formate
4. UI/UX Verbesserungen

Entwickle diese Anwendung schrittweise und modular, sodass jedes Modul einzeln testbar und erweiterbar ist. Beginne mit der Kern-Funktionalität und baue darauf auf.