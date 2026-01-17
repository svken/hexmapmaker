# Hex Map Editor

A simple yet powerful Python-based hexagonal map editor with a graphical user interface for creating, editing, and exporting hex-based game maps.

## Overview

This editor provides an intuitive interface for designing hexagonal grid maps with support for terrain types, faction control, resource management, and strategic gameplay elements. Originally developed for integration with the Godot game engine, it features a modular architecture that makes it extensible for various game projects.

## Features

- **Interactive Hex Grid**: Pointy-top hexagonal grid with zoom and pan functionality
- **Terrain Editing**: Paint different terrain types with customizable brush sizes
- **Faction System**: Assign territories to different factions with visual indicators  
- **Resource Management**: Place and configure resource nodes (steel, population, etc.)
- **Strategic Elements**: Set elevation, temperature, fertility, and accessibility values
- **Export Support**: Export maps in formats compatible with Godot and other game engines
- **Modular Design**: Clean separation of concerns with dedicated modules for data, UI, utilities, and export

## Project Structure

```
mapmaker/
├── app.py              # Main application entry point
├── main.py             # Legacy entry point (deprecated)
├── data/               # Data models and grid management
│   ├── models.py       # Tile, Area, and Faction data classes
│   └── grid_manager.py # Grid operations and management
├── ui/                 # User interface components
│   ├── main_window.py  # Main application window
│   ├── map_canvas.py   # Interactive hex grid canvas
│   ├── dialogs.py      # Modal dialogs and forms
│   └── event_handlers.py # UI event handling
├── utils/              # Utility functions
│   └── hex_math.py     # Hexagonal grid mathematics
└── export/             # Export functionality
    └── godot_exporter.py # Godot-compatible export formats
```

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- Standard Python libraries (math, typing, etc.)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/svken/mapmaker.git
   cd mapmaker
   ```

2. Run the application:
   ```bash
   python app.py
   ```

## Usage

- **Navigation**: Use mouse wheel to zoom, click and drag to pan around the map
- **Terrain Painting**: Select a terrain type and paint on the hex grid
- **Faction Control**: Switch to faction mode to assign territories
- **Brush Size**: Adjust brush size for painting multiple hexes at once
- **Export**: Use the export menu to save your map in various formats

## Map Data Format

The editor uses a comprehensive tile-based data structure supporting:
- Coordinate systems (odd-q offset for pointy-top hexes)
- Terrain and area types with customizable properties
- Faction assignments and military attributes
- Resource systems with regeneration rates
- Strategic gameplay elements (elevation, temperature, fertility)
- Structure placement and population management

## Contributing

This is a simple editor project. Feel free to fork and extend it for your own game development needs.

## License

Open source - use and modify as needed for your projects.