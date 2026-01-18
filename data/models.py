"""
Datenmodelle für den Hex Map Editor
Basiert auf den Godot-Projektstrukturen
"""
from typing import Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field, field


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

class StrategicRoleType(Enum):
    """Strategische Rollen für Tiles"""
    FIREPOWER = "firepower"
    MOBILITY = "mobility"
    INTEL = "intel"
    RAILWAY = "railway"
    LOGISTIC_HUB = "logistic_hub"
    HEADQUARTER = "headquarter"
    NONE = "none"


@dataclass
class Area:
    """Terrain-Typ Definition"""
    id: str
    display_name: str
    color: str = "#ffffff"  # Hex-Farbe für Darstellung


@dataclass  
class Tile:
    """Hex-Tile mit wesentlichen Eigenschaften"""
    coordinates: Tuple[int, int] = (0, 0)
    area: Optional[Area] = None
    is_land: bool = True
    faction: FactionType = FactionType.NEUTRAL
    strategic_role: StrategicRoleType = StrategicRoleType.NONE
    production: int = 0  # Produktion für firepower, intel, mobility


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
        water_area = next(
            (area for area in self.area_definitions if area.id == "water"),
            self.area_definitions[0] if self.area_definitions else None
        )
        
        for y in range(self.height):
            for x in range(self.width):
                tile = Tile(
                    coordinates=(x, y),
                    area=water_area,
                    is_land=False  # Wasser ist kein Land
                )
                self.tiles.append(tile)


def get_default_areas() -> List[Area]:
    """Standard Terrain-Typen"""
    return [
        Area("desert", "Desert", "#f4e3a5"),
        Area("plain", "Plain", "#90c695"),
        Area("mountains", "Mountains", "#8b7355"),
        Area("city", "City", "#888888"),
        Area("water", "Water", "#4682b4"),
    ]