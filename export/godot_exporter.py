"""
Export-Funktionalität für JSON Dateien
"""
import os
import json
from tkinter import filedialog, messagebox
from data.grid_manager import GridManager


class MapExporter:
    """Exportiert Hex-Karten als JSON Dateien"""
    
    def __init__(self, grid_manager: GridManager):
        self.grid_manager = grid_manager
    
    def export_map(self):
        """Exportiert die Karte als JSON Datei"""
        file_path = filedialog.asksaveasfilename(
            title="Export Hex Map",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self._write_json_file(file_path)
            messagebox.showinfo("Export Success", f"Map exported successfully to:\\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export map:\\n{str(e)}")
            return False
    
    def _write_json_file(self, file_path: str):
        """Schreibt die Karte als JSON Datei"""
        grid = self.grid_manager.grid
        
        # Sammle alle Tile-Daten
        map_data = []
        
        for tile in grid.tiles:
            tile_data = self._extract_tile_data(tile)
            map_data.append(tile_data)
        
        # Erstelle das finale JSON-Objekt
        json_data = {
            "map": map_data
        }
        
        # Schreibe JSON Datei
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def _extract_tile_data(self, tile):
        """Extrahiert die relevanten Daten aus einem Tile"""
        # Koordinaten extrahieren
        coords = [0, 0]
        if hasattr(tile, 'coordinates') and tile.coordinates:
            coords = [tile.coordinates[0], tile.coordinates[1]]
        
        # Area extrahieren
        area = None
        if hasattr(tile, 'area') and tile.area and hasattr(tile.area, 'id'):
            area = tile.area.id
        
        # Faction extrahieren
        faction = "neutral"
        if hasattr(tile, 'faction'):
            if hasattr(tile.faction, 'value'):
                faction = tile.faction.value
            else:
                faction = str(tile.faction).lower()
        
        return {
            "coords": coords,
            "area": area,
            "faction": faction
        }