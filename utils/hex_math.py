"""
Hex-Mathematik Funktionen
Implementiert das odd-r offset System aus dem Godot-Projekt
"""
import math
from typing import Tuple, List


class HexMath:
    """Hex-Koordinaten Mathematik"""
    
    @staticmethod
    def get_hex_neighbors_in_radius(center_x: int, center_y: int, radius: int) -> List[Tuple[int, int]]:
        """
        Gibt alle Hex-Tiles in einem bestimmten Radius zurück
        
        Args:
            center_x: Zentrum X-Koordinate
            center_y: Zentrum Y-Koordinate  
            radius: Radius (0 = nur Zentrum, 1 = Zentrum + direkte Nachbarn, etc.)
            
        Returns:
            Liste aller Tile-Koordinaten im Radius
        """
        center_x = int(center_x)
        center_y = int(center_y)
        radius = int(radius)
        
        if radius <= 0:
            return [(center_x, center_y)]
        
        tiles = [(center_x, center_y)]
        visited = {(center_x, center_y)}
        
        # Breadth-first search für alle Tiles im Radius
        current_ring = [(center_x, center_y)]
        
        for ring in range(radius):
            next_ring = []
            for tile_x, tile_y in current_ring:
                neighbors = HexMath.get_hex_neighbors(tile_x, tile_y)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        tiles.append(neighbor)
                        next_ring.append(neighbor)
            current_ring = next_ring
            
        return tiles
    
    @staticmethod
    def get_hex_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
        """
        Hex-Nachbarn für odd-r offset System
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            Liste der Nachbar-Koordinaten
        """
        # Ensure x and y are integers
        x = int(x)
        y = int(y)
        
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
    
    @staticmethod
    def hex_to_pixel(x: int, y: int, hex_size: float = 20.0) -> Tuple[float, float]:
        """
        Konvertiert Hex-Koordinaten zu Pixel-Koordinaten (odd-r offset)
        
        Args:
            x: Hex X-Koordinate
            y: Hex Y-Koordinate
            hex_size: Größe der Hexagone
            
        Returns:
            (pixel_x, pixel_y) Tuple
        """
        # Ensure x and y are integers
        x = int(x)
        y = int(y)
        
        # odd-r offset layout (flat-top hexes)
        pixel_x = hex_size * (3.0 / 2.0) * x
        pixel_y = hex_size * math.sqrt(3.0) * (y + 0.5 * (x & 1))
        
        return pixel_x, pixel_y
    
    @staticmethod
    def pixel_to_hex(pixel_x: float, pixel_y: float, hex_size: float = 20.0) -> Tuple[int, int]:
        """
        Konvertiert Pixel-Koordinaten zu Hex-Koordinaten (odd-r offset)
        
        Args:
            pixel_x: Pixel X-Position
            pixel_y: Pixel Y-Position
            hex_size: Größe der Hexagone
            
        Returns:
            (hex_x, hex_y) Tuple
        """
        # Direkte Umkehrung der hex_to_pixel Formel für odd-r layout
        # pixel_x = hex_size * (3.0 / 2.0) * x
        # pixel_y = hex_size * sqrt(3) * (y + 0.5 * (x & 1))
        
        # X-Koordinate ist einfach
        hex_x_float = pixel_x / (hex_size * 3.0 / 2.0)
        hex_x = round(hex_x_float)
        
        # Y-Koordinate berücksichtigt den offset für ungerade Spalten
        offset = 0.5 * (hex_x & 1)
        hex_y_float = (pixel_y / (hex_size * math.sqrt(3.0))) - offset
        hex_y = round(hex_y_float)
        
        return hex_x, hex_y
    
    @staticmethod
    def get_hex_vertices(center_x: float, center_y: float, hex_size: float) -> List[Tuple[float, float]]:
        """
        Berechnet die 6 Eckpunkte eines Hexagons
        
        Args:
            center_x: Zentrum X
            center_y: Zentrum Y
            hex_size: Größe des Hexagons
            
        Returns:
            Liste von 6 Eckpunkten
        """
        vertices = []
        for i in range(6):
            angle = math.pi / 3.0 * i  # 60 Grad Schritte
            vertex_x = center_x + hex_size * math.cos(angle)
            vertex_y = center_y + hex_size * math.sin(angle)
            vertices.append((vertex_x, vertex_y))
        return vertices
    
    @staticmethod
    def hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
        """
        Berechnet die Distanz zwischen zwei Hex-Koordinaten
        
        Args:
            x1, y1: Erste Koordinate
            x2, y2: Zweite Koordinate
            
        Returns:
            Hex-Distanz
        """
        # Konvertiere zu cube coordinates für einfachere Distanz-Berechnung
        def offset_to_cube(col: int, row: int) -> Tuple[int, int, int]:
            q = col
            r = row - (col + (col & 1)) // 2
            s = -q - r
            return q, r, s
        
        q1, r1, s1 = offset_to_cube(x1, y1)
        q2, r2, s2 = offset_to_cube(x2, y2)
        
        return (abs(q1 - q2) + abs(r1 - r2) + abs(s1 - s2)) // 2