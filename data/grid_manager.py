"""
Grid-Manager für Hex-Karten
Verwaltet die Erstellung und Manipulation von Hex-Grids
"""
from typing import Optional, Tuple
from data.models import Grid, Tile, Area, get_default_areas
from utils.hex_math import HexMath


class GridManager:
    """Verwaltet Hex-Grid Operationen"""
    
    def __init__(self, grid: Optional[Grid] = None):
        """
        Initialisiert den GridManager
        
        Args:
            grid: Bestehendes Grid oder None für neues Grid
        """
        self.grid = grid if grid is not None else Grid()
    
    def create_new_grid(self, width: int, height: int) -> Grid:
        """
        Erstellt ein neues leeres Grid
        
        Args:
            width: Breite des Grids
            height: Höhe des Grids
            
        Returns:
            Neues Grid-Objekt
        """
        self.grid = Grid(width=width, height=height)
        return self.grid
    
    def get_tile_at(self, x: int, y: int) -> Optional[Tile]:
        """
        Holt ein Tile an den gegebenen Koordinaten
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            Tile-Objekt oder None falls außerhalb der Grenzen
        """
        if not self._is_valid_coordinate(x, y):
            return None
        
        index = y * self.grid.width + x
        if 0 <= index < len(self.grid.tiles):
            return self.grid.tiles[index]
        return None
    
    def set_tile_area(self, x: int, y: int, area: Area) -> bool:
        """
        Setzt den Terrain-Typ für ein Tile
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            area: Neuer Terrain-Typ
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        tile = self.get_tile_at(x, y)
        if tile is not None:
            tile.area = area
            return True
        return False
    
    def get_neighbors(self, x: int, y: int) -> list[Tile]:
        """
        Holt alle Nachbar-Tiles eines Tiles
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            Liste der Nachbar-Tiles
        """
        neighbors = []
        neighbor_coords = HexMath.get_hex_neighbors(x, y)
        
        for nx, ny in neighbor_coords:
            tile = self.get_tile_at(nx, ny)
            if tile is not None:
                neighbors.append(tile)
                
        return neighbors
    
    def _is_valid_coordinate(self, x: int, y: int) -> bool:
        """
        Prüft ob Koordinaten im gültigen Bereich liegen
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            True wenn gültig, False sonst
        """
        return 0 <= x < self.grid.width and 0 <= y < self.grid.height
    
    def get_grid_bounds(self) -> Tuple[int, int, int, int]:
        """
        Gibt die Grenzen des Grids zurück
        
        Returns:
            (min_x, min_y, max_x, max_y) Tuple
        """
        return 0, 0, self.grid.width - 1, self.grid.height - 1
    
    def get_all_tiles(self) -> list[Tile]:
        """
        Gibt alle Tiles des Grids zurück
        
        Returns:
            Liste aller Tiles
        """
        return self.grid.tiles.copy()