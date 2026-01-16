"""
Event Handler für die Hauptanwendung
"""
from typing import Optional
from data.models import Tile


class EventHandlers:
    """Event Handler für Map Canvas und UI Interaktionen"""
    
    def __init__(self, main_window, grid_manager, map_canvas):
        self.main_window = main_window
        self.grid_manager = grid_manager
        self.map_canvas = map_canvas
        
        # Event-Callbacks setzen
        self.map_canvas.on_tile_hover = self._on_tile_hover
        self.map_canvas.on_tile_paint = self._on_terrain_painted
        self.map_canvas.on_faction_paint = self._on_faction_painted
    
    def _on_tile_hover(self, tile: Optional[Tile]):
        """Wird aufgerufen wenn Maus über Tile hovert"""
        if tile:
            # Tile-Eigenschaften formatieren
            properties_text = self._format_tile_properties(tile)
            self.main_window.update_properties(properties_text)
        else:
            self.main_window.update_properties("No tile selected")
    
    def _on_terrain_painted(self, tile: Tile, old_area):
        """Wird aufgerufen wenn ein Tile mit Terrain bemalt wurde"""
        terrain_name = tile.area.name if tile.area else "Unknown"
        coords_text = f"Painted {terrain_name} at ({tile.coordinates[0]}, {tile.coordinates[1]})"
        self.main_window.set_status(coords_text)
    
    def _on_faction_painted(self, tile: Tile, old_faction):
        """Wird aufgerufen wenn ein Tile mit Faction bemalt wurde"""
        faction_name = tile.faction.value
        coords_text = f"Painted faction {faction_name} at ({tile.coordinates[0]}, {tile.coordinates[1]})"
        self.main_window.set_status(coords_text)
    
    def _format_tile_properties(self, tile: Tile) -> str:
        """Formatiert Tile-Eigenschaften für Anzeige"""
        lines = []
        lines.append(f"=== TILE PROPERTIES ===")
        lines.append(f"Coordinates: {tile.coordinates}")
        
        if tile.area:
            lines.append(f"\\nTerrain: {tile.area.name}")
            lines.append(f"  ID: {tile.area.id}")
            lines.append(f"  Color: {tile.area.color}")
            lines.append(f"  Movement Cost: {tile.area.movement_cost}")
            lines.append(f"  Resource Mult: {tile.area.resource_mult}")
            lines.append(f"  Attack Mult: {tile.area.attack_mult}")
            lines.append(f"  Defense Mult: {tile.area.defense_mult}")
        
        lines.append(f"\\nGeneral:")
        lines.append(f"  Is Land: {tile.is_land}")
        lines.append(f"  Faction: {tile.faction.value}")
        
        lines.append(f"\\nResources:")
        lines.append(f"  Type: {tile.resource.value}")
        lines.append(f"  Count: {tile.resource_count:.1f}")
        lines.append(f"  Regeneration: {tile.resource_regeneration_rate:.1f}/turn")
        lines.append(f"  Max Capacity: {tile.max_resource_capacity:.1f}")
        
        lines.append(f"\\nMilitary:")
        lines.append(f"  In Battle: {tile.in_battle}")
        lines.append(f"  Strength: {tile.strength:.1f}")
        lines.append(f"  Fortification Level: {tile.fortification_level}")
        lines.append(f"  Garrison Size: {tile.garrison_size}")
        
        lines.append(f"\\nEnvironment:")
        lines.append(f"  Elevation: {tile.elevation:.1f}m")
        lines.append(f"  Temperature: {tile.temperature:.1f}°C")
        lines.append(f"  Fertility: {tile.fertility:.1f}")
        
        return "\\n".join(lines)