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
    
    def load_map(self):
        """Lädt eine Karte aus einer JSON Datei"""
        file_path = filedialog.askopenfilename(
            title="Load Hex Map",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self._read_json_file(file_path)
            messagebox.showinfo("Load Success", f"Map loaded successfully from:\\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load map:\\n{str(e)}")
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

        # Strategic Role extrahieren
        strategic_role = "none"
        if hasattr(tile, 'strategic_role'):
            if hasattr(tile.strategic_role, 'value'):
                strategic_role = tile.strategic_role.value
            else:
                strategic_role = str(tile.strategic_role).lower()
        
        return {
            "coords": coords,
            "area": area,
            "faction": faction,
            "strategic_role": strategic_role
        }
    
    def _read_json_file(self, file_path: str):
        """Lädt Karten-Daten aus einer JSON Datei"""
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if "map" not in json_data:
            raise ValueError("JSON file must contain a 'map' array")
        
        map_data = json_data["map"]
        grid = self.grid_manager.grid
        
        # Update existing tiles with loaded data
        for tile_data in map_data:
            self._update_tile_from_data(tile_data, grid)
    
    def _update_tile_from_data(self, tile_data: dict, grid):
        """Aktualisiert ein Tile mit Daten aus der JSON"""
        if "coords" not in tile_data:
            return
        
        coords = tile_data["coords"]
        if len(coords) != 2:
            return
            
        x, y = coords[0], coords[1]
        
        # Finde das entsprechende Tile im Grid
        tile_index = y * grid.width + x
        if 0 <= tile_index < len(grid.tiles):
            tile = grid.tiles[tile_index]
            
            # Update Area
            if "area" in tile_data and tile_data["area"]:
                area_id = tile_data["area"]
                # Finde die Area in den area_definitions
                for area in grid.area_definitions:
                    if area.id == area_id:
                        tile.area = area
                        break
            
            # Update Faction
            if "faction" in tile_data:
                from data.models import FactionType
                faction_str = tile_data["faction"]
                try:
                    tile.faction = FactionType(faction_str)
                except ValueError:
                    tile.faction = FactionType.NEUTRAL

            # Update Strategic Role
            if "strategic_role" in tile_data:
                from data.models import StrategicRoleType
                role_str = tile_data["strategic_role"]
                try:
                    tile.strategic_role = StrategicRoleType(role_str)
                except ValueError:
                    tile.strategic_role = StrategicRoleType.NONE