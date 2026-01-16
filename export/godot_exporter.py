"""
Export-Funktionalität für Godot .tres Dateien
"""
import os
from tkinter import filedialog, messagebox
from data.grid_manager import GridManager


class MapExporter:
    """Exportiert Hex-Karten als Godot .tres Resource-Dateien"""
    
    def __init__(self, grid_manager: GridManager):
        self.grid_manager = grid_manager
    
    def export_to_godot(self):
        """Exportiert die Karte als .tres Datei für Godot"""
        file_path = filedialog.asksaveasfilename(
            title="Export Hex Map",
            defaultextension=".tres",
            filetypes=[("Godot Resource", "*.tres"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self._write_godot_resource(file_path)
            messagebox.showinfo("Export Success", f"Map exported successfully to:\\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export map:\\n{str(e)}")
            return False
    
    def _write_godot_resource(self, file_path: str):
        """Schreibt die Karte als Godot .tres Resource"""
        grid = self.grid_manager.grid
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Godot Resource Header
            f.write('[gd_resource type="Resource" script_class="HexGrid" ')
            f.write('script="res://scripts/HexGrid.gd" format=3]\\n\\n')
            
            # Grid-Eigenschaften
            f.write('[resource]\\n')
            f.write(f'grid_width = {grid.width}\\n')
            f.write(f'grid_height = {grid.height}\\n')
            
            # Tiles Array
            f.write('tiles = [\\n')
            
            # Vereinfachte, sichere Tile-Verarbeitung
            for i, tile in enumerate(grid.tiles):
                self._write_tile(f, tile, i, len(grid.tiles))
            
            f.write(']\\n')
    
    def _write_tile(self, f, tile, index: int, total_tiles: int):
        """Schreibt ein einzelnes Tile sicher"""
        try:
            # Extrahiere Koordinaten sicher
            if hasattr(tile, 'coordinates') and tile.coordinates:
                x, y = tile.coordinates[0], tile.coordinates[1]
            else:
                x, y = 0, 0
            
            # Extrahiere Area ID sicher
            area_id = 'water'  # Standard
            if hasattr(tile, 'area') and tile.area and hasattr(tile.area, 'id'):
                area_id = str(tile.area.id)
            
            # Extrahiere Faction sicher
            faction = 'neutral'  # Standard
            if hasattr(tile, 'faction'):
                if hasattr(tile.faction, 'value'):
                    faction = str(tile.faction.value)
                else:
                    faction = str(tile.faction).lower()
            
            # Extrahiere is_land sicher
            is_land = True  # Standard
            if hasattr(tile, 'is_land'):
                is_land = bool(tile.is_land)
            
            # Extrahiere Resources sicher
            resources = []
            if hasattr(tile, 'resource') and tile.resource:
                try:
                    if hasattr(tile.resource, 'value') and tile.resource.value != 'none':
                        resources = [str(tile.resource.value)]
                except (AttributeError, ValueError):
                    pass
            
            # Schreibe Tile
            f.write('\\t{\\n')
            f.write(f'\\t\\t"coordinates": [{x}, {y}],\\n')
            f.write(f'\\t\\t"area_id": "{area_id}",\\n')
            f.write(f'\\t\\t"faction": "{faction}",\\n')
            f.write(f'\\t\\t"is_land": {"true" if is_land else "false"},\\n')
            
            # Resources Array
            if resources:
                resources_str = '", "'.join(resources)
                f.write(f'\\t\\t"resources": ["{resources_str}"]\\n')
            else:
                f.write(f'\\t\\t"resources": []\\n')
            
            # Schließe Tile
            if index < total_tiles - 1:
                f.write('\\t},\\n')
            else:
                f.write('\\t}\\n')
                
        except Exception as e:
            print(f"Skipping tile {index}: {e}")
            # Schreibe leeres Tile als Fallback
            f.write('\\t{\\n')
            f.write('\\t\\t"coordinates": [0, 0],\\n')
            f.write('\\t\\t"area_id": "water",\\n')
            f.write('\\t\\t"faction": "neutral",\\n')
            f.write('\\t\\t"is_land": false,\\n')
            f.write('\\t\\t"resources": []\\n')
            f.write('\\t}')
            if index < total_tiles - 1:
                f.write(',')
            f.write('\\n')