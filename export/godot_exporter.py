"""
Export-Funktionalität für JSON Dateien
"""
import os
import json
from tkinter import filedialog, messagebox
from data.grid_manager import GridManager


class MapExporter:
    """Exportiert Hex-Karten als JSON Dateien"""
    
    def __init__(self, grid_manager: GridManager, map_canvas=None):
        self.grid_manager = grid_manager
        self.map_canvas = map_canvas
    
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
        
        # Canvas-Einstellungen sammeln
        canvas_settings = {"hex_size": 15.0}  # Default
        if self.map_canvas and hasattr(self.map_canvas, 'hex_size'):
            canvas_settings["hex_size"] = self.map_canvas.hex_size
        
        # Erstelle das finale JSON-Objekt mit Metadaten
        json_data = {
            "metadata": {
                "grid_width": grid.width,
                "grid_height": grid.height,
                "canvas_settings": canvas_settings
            },
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
        
        # Production extrahieren
        production = 0
        if hasattr(tile, 'production'):
            production = tile.production
        
        return {
            "coords": coords,
            "area": area,
            "faction": faction,
            "strategic_role": strategic_role,
            "production": production
        }
    
    def _read_json_file(self, file_path: str):
        """Lädt Karten-Daten aus einer JSON Datei"""
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if "map" not in json_data:
            raise ValueError("JSON file must contain a 'map' array")
        
        # Lade Metadaten falls vorhanden
        if "metadata" in json_data:
            metadata = json_data["metadata"]
            
            # Grid-Größe anpassen falls nötig
            if "grid_width" in metadata and "grid_height" in metadata:
                new_width = metadata["grid_width"]
                new_height = metadata["grid_height"]
                
                # Grid neu erstellen falls Größe sich geändert hat
                current_grid = self.grid_manager.grid
                if current_grid.width != new_width or current_grid.height != new_height:
                    self.grid_manager.create_new_grid(new_width, new_height)
            
            # Canvas-Einstellungen anwenden
            if "canvas_settings" in metadata and self.map_canvas:
                canvas_settings = metadata["canvas_settings"]
                if "hex_size" in canvas_settings:
                    self.map_canvas.set_hex_size(canvas_settings["hex_size"])
        
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
            
            # Update Production
            if "production" in tile_data:
                try:
                    tile.production = int(tile_data["production"])
                except (ValueError, TypeError):
                    tile.production = 0