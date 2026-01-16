"""
Datenmodelle für den Hex Map Editor
Basiert auf den Godot-Projektstrukturen
"""
from typing import Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field


class ResourceType(Enum):
    """Ressourcen-Typen"""
    NONE = "none"
    STEEL = "steel"
    HUMANS = "humans"


class FactionType(Enum):
    """Fraktions-Typen"""
    NEUTRAL = "neutral"
    BLUE = "blue"
    RED = "red"


@dataclass
class Area:
    """Terrain-Typ Definition"""
    id: str
    display_name: str
    move_cost: int
    attack_mult: float
    defense_mult: float
    color: str = "#ffffff"  # Hex-Farbe für Darstellung


@dataclass  
class Tile:
    """Hex-Tile mit allen Eigenschaften"""
    # Grundlegende Eigenschaften
    coordinates: Tuple[int, int]
    area: Optional[Area] = None
    is_land: bool = True
    
    # Ressourcen System
    resource: ResourceType = ResourceType.NONE
    resource_count: float = 0.0
    resource_regeneration_rate: float = 0.1
    max_resource_capacity: float = 10.0
    
    # Militär und Kampf
    faction: FactionType = FactionType.NEUTRAL
    in_battle: bool = False
    front_degree: int = 0
    strength: float = 0.0
    fortification_level: int = 0
    garrison_size: int = 0
    
    # Erweiterte Eigenschaften
    elevation: float = 0.0
    temperature: float = 20.0
    fertility: float = 1.0
    accessibility: float = 1.0
    
    # Strukturen
    structures: List[str] = field(default_factory=list)
    population: int = 0
    happiness: float = 50.0
    
    # Strategische Information
    strategic_value: int = 1
    supply_lines: List[Tuple[int, int]] = field(default_factory=list)
    visibility: int = 1
    
    # UI
    is_selected: bool = False
    neighbour_tiles: int = 0


@dataclass
class Grid:
    """Hex-Grid Container"""
    width: int = 50
    height: int = 50
    tiles: List[Tile] = field(default_factory=list)
    area_definitions: List[Area] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialisiere Standard-Terrain-Typen"""
        if not self.area_definitions:
            self.area_definitions = get_default_areas()
        
        # Tiles initialisieren falls leer
        if not self.tiles:
            self._initialize_tiles()
    
    def _initialize_tiles(self):
        """Erstelle leere Tiles für das Grid"""
        plain_area = next(
            (area for area in self.area_definitions if area.id == "plain"),
            self.area_definitions[0] if self.area_definitions else None
        )
        
        for y in range(self.height):
            for x in range(self.width):
                tile = Tile(
                    coordinates=(x, y),
                    area=plain_area
                )
                self.tiles.append(tile)


def get_default_areas() -> List[Area]:
    """Standard Terrain-Typen"""
    return [
        Area("desert", "Desert", 3, 0.8, 0.9, "#f4e3a5"),
        Area("plain", "Plain", 3, 0.8, 0.9, "#90c695"),
        Area("mountains", "Mountains", 4, 10.0, 20.0, "#8b7355"),
        Area("city", "City", 2, 0.9, 1.4, "#888888"),
        Area("water", "Water", 100, 0.0, 0.0, "#4682b4"),
    ]