"""
Hex-Karten Canvas für die GUI
Zeigt Hex-Grid an mit Zoom und Pan-Funktionalität
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Callable
import math

from data.grid_manager import GridManager
from data.models import Tile
from utils.hex_math import HexMath


class MapCanvas:
    """Canvas für Hex-Karten Darstellung"""
    
    def __init__(self, parent: tk.Widget, grid_manager: GridManager):
        """
        Initialisiert den Map Canvas
        
        Args:
            parent: Parent-Widget
            grid_manager: GridManager-Instanz
        """
        self.parent = parent
        self.grid_manager = grid_manager
        
        # Canvas-Einstellungen
        self.canvas = tk.Canvas(
            parent,
            bg='#2d2d30',
            width=800,
            height=600
        )
        
        # Hex-Darstellungsparameter
        self.hex_size = 15.0
        self.min_hex_size = 5.0
        self.max_hex_size = 50.0
        
        # Kamera/View Parameter
        self.view_x = 0.0
        self.view_y = 0.0
        self.zoom_factor = 1.0
        
        # Mouse-Tracking für Pan
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_dragging = False
        
        # Paint-Tool Parameter
        self.paint_mode = False
        self.is_painting = False
        self.selected_terrain = None
        self.last_painted_tile = None
        
        # Callbacks
        self.on_tile_hover: Optional[Callable[[Optional[Tile]], None]] = None
        self.on_tile_click: Optional[Callable[[Tile], None]] = None
        self.on_tile_paint: Optional[Callable[[Tile, any], None]] = None
        
        # Event-Bindings
        self._bind_events()
        
        # Initialer Render
        self.render_map()
    
    def _bind_events(self):
        """Bindet Mouse- und Keyboard-Events"""
        # Mouse-Events für Pan und Paint
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        
        # Mouse-Events für Zoom
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux
        
        # Mouse-Motion für Hover
        self.canvas.bind("<Motion>", self._on_mouse_motion)
        
        # Focus für Keyboard-Events
        self.canvas.focus_set()
        self.canvas.bind("<KeyPress>", self._on_key_press)
        self.canvas.config(highlightthickness=0)
        
        # Mache Canvas fokussierbar
        self.canvas.config(takefocus=True)
    
    def _on_mouse_down(self, event):
        """Mouse-Button gedrückt"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.is_dragging = False  # Erst bei Bewegung auf True setzen
        
        # Focus setzen
        self.canvas.focus_set()
        
        # Paint-Mode aktivieren wenn Pinsel aktiv
        if self.paint_mode and self.selected_terrain:
            self.is_painting = True
            tile = self._get_tile_at_pixel(event.x, event.y)
            if tile:
                self._paint_tile(tile)
                self.last_painted_tile = tile
        
        # Click wird in mouse_up behandelt für saubere Trennung
    
    def _on_mouse_drag(self, event):
        """Mouse-Drag für Panning oder Painting"""
        # Erst ab einer gewissen Bewegung als Drag behandeln
        if not self.is_dragging:
            dx = abs(event.x - self.last_mouse_x)
            dy = abs(event.y - self.last_mouse_y)
            if dx > 3 or dy > 3:  # Mindestbewegung für Drag
                self.is_dragging = True
        
        if self.is_painting and self.paint_mode and self.selected_terrain:
            # Paint-Mode: Male über alle Tiles die der Cursor berührt
            tile = self._get_tile_at_pixel(event.x, event.y)
            if tile and tile != self.last_painted_tile:
                self._paint_tile(tile)
                self.last_painted_tile = tile
        elif self.is_dragging and not self.is_painting:
            # Normal Pan-Mode
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            # Pan die View
            self.view_x -= dx / self.zoom_factor
            self.view_y -= dy / self.zoom_factor
            
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
            self.render_map()
    
    def _on_mouse_up(self, event):
        """Mouse-Button losgelassen"""
        was_dragging = self.is_dragging
        was_painting = self.is_painting
        
        self.is_dragging = False
        self.is_painting = False
        self.last_painted_tile = None
        
        # Wenn nicht gedragt und nicht gemalt wurde, als Click behandeln
        if not was_dragging and not was_painting:
            tile = self._get_tile_at_pixel(event.x, event.y)
            if tile and self.on_tile_click:
                self.on_tile_click(tile)
    
    def _on_mouse_wheel(self, event):
        """Mouse-Wheel für Zoom"""
        # Zoom-Faktor berechnen
        if event.delta > 0 or event.num == 4:  # Zoom in
            zoom_delta = 1.1
        else:  # Zoom out
            zoom_delta = 0.9
        
        # Zoom um Mouse-Position
        mouse_x = event.x
        mouse_y = event.y
        
        # Weltkoordinaten vor Zoom
        world_x = (mouse_x / self.zoom_factor) + self.view_x
        world_y = (mouse_y / self.zoom_factor) + self.view_y
        
        # Neuen Zoom-Faktor anwenden (mit Limits)
        new_hex_size = self.hex_size * zoom_delta
        if self.min_hex_size <= new_hex_size <= self.max_hex_size:
            self.hex_size = new_hex_size
            self.zoom_factor *= zoom_delta
            
            # View anpassen um Mouse-Position stabil zu halten
            self.view_x = world_x - (mouse_x / self.zoom_factor)
            self.view_y = world_y - (mouse_y / self.zoom_factor)
            
            self.render_map()
    
    def _on_mouse_motion(self, event):
        """Mouse-Motion für Hover"""
        if not self.is_dragging:
            tile = self._get_tile_at_pixel(event.x, event.y)
            if self.on_tile_hover:
                self.on_tile_hover(tile)
    
    def _on_key_press(self, event):
        """Keyboard-Input"""
        # WASD für Panning
        pan_speed = 50.0 / self.zoom_factor
        
        if event.keysym == 'w':
            self.view_y -= pan_speed
        elif event.keysym == 's':
            self.view_y += pan_speed
        elif event.keysym == 'a':
            self.view_x -= pan_speed
        elif event.keysym == 'd':
            self.view_x += pan_speed
        elif event.keysym == 'r':  # Reset View
            self.reset_view()
        else:
            return
        
        self.render_map()
    
    def _get_tile_at_pixel(self, pixel_x: int, pixel_y: int) -> Optional[Tile]:
        """
        Findet das Tile an der Pixel-Position
        
        Args:
            pixel_x: X-Pixel-Koordinate
            pixel_y: Y-Pixel-Koordinate
            
        Returns:
            Tile oder None
        """
        # Pixel zu Welt-Koordinaten
        world_x = (pixel_x / self.zoom_factor) + self.view_x
        world_y = (pixel_y / self.zoom_factor) + self.view_y
        
        # Welt zu Hex-Koordinaten
        hex_x, hex_y = HexMath.pixel_to_hex(world_x, world_y, self.hex_size)
        
        return self.grid_manager.get_tile_at(hex_x, hex_y)
    
    def render_map(self):
        """Rendert die komplette Hex-Karte"""
        # Canvas löschen
        self.canvas.delete("all")
        
        # Canvas-Größe aktualisieren
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas noch nicht initialisiert - versuche es später nochmal
            self.canvas.after(100, self.render_map)
            return
        
        # Sichtbare Hex-Bereiche berechnen
        visible_hexes = self._get_visible_hexes(canvas_width, canvas_height)
        
        # Alle sichtbaren Hexagone rendern
        for hex_x, hex_y in visible_hexes:
            tile = self.grid_manager.get_tile_at(hex_x, hex_y)
            if tile:
                self._render_hex(hex_x, hex_y, tile)
        
        # Grid-Info anzeigen
        self._render_debug_info()
    
    def _get_visible_hexes(self, canvas_width: int, canvas_height: int) -> list[Tuple[int, int]]:
        """
        Berechnet welche Hexagone sichtbar sind
        
        Args:
            canvas_width: Canvas-Breite
            canvas_height: Canvas-Höhe
            
        Returns:
            Liste von (hex_x, hex_y) Tupeln
        """
        visible_hexes = []
        
        # Erweiterten Bereich berechnen für Sicherheit
        margin = 2
        
        # Grid-Grenzen
        min_x, min_y, max_x, max_y = self.grid_manager.get_grid_bounds()
        
        # Alle Tiles im Grid prüfen (für kleine Grids einfacher)
        for y in range(max(0, min_y - margin), min(max_y + margin + 1, self.grid_manager.grid.height)):
            for x in range(max(0, min_x - margin), min(max_x + margin + 1, self.grid_manager.grid.width)):
                # Hex zu Pixel für Sichtbarkeits-Check
                world_x, world_y = HexMath.hex_to_pixel(x, y, self.hex_size)
                screen_x = (world_x - self.view_x) * self.zoom_factor
                screen_y = (world_y - self.view_y) * self.zoom_factor
                
                # Check ob auf dem Bildschirm
                hex_screen_size = self.hex_size * self.zoom_factor
                if (-hex_screen_size <= screen_x <= canvas_width + hex_screen_size and
                    -hex_screen_size <= screen_y <= canvas_height + hex_screen_size):
                    visible_hexes.append((x, y))
        
        return visible_hexes
    
    def _render_hex(self, hex_x: int, hex_y: int, tile: Tile):
        """
        Rendert ein einzelnes Hexagon
        
        Args:
            hex_x: Hex X-Koordinate
            hex_y: Hex Y-Koordinate
            tile: Tile-Objekt
        """
        # Hex-Position in Welt-Koordinaten
        world_x, world_y = HexMath.hex_to_pixel(hex_x, hex_y, self.hex_size)
        
        # Welt zu Screen-Koordinaten
        screen_x = (world_x - self.view_x) * self.zoom_factor
        screen_y = (world_y - self.view_y) * self.zoom_factor
        
        # Hex-Eckpunkte berechnen
        hex_vertices = HexMath.get_hex_vertices(screen_x, screen_y, self.hex_size * self.zoom_factor)
        
        # Flache Liste für tkinter
        coords = []
        for vx, vy in hex_vertices:
            coords.extend([vx, vy])
        
        # Farbe bestimmen
        fill_color = "#90c695"  # Standard grün
        if tile.area:
            fill_color = tile.area.color
        
        outline_color = "#404040"
        line_width = 1
        
        # Hervorhebung für ausgewähltes Tile
        if tile.is_selected:
            outline_color = "#ffffff"
            line_width = 2
        
        # Hexagon zeichnen
        self.canvas.create_polygon(
            coords,
            fill=fill_color,
            outline=outline_color,
            width=line_width,
            tags=f"hex_{hex_x}_{hex_y}"
        )
        
        # Koordinaten anzeigen (nur bei großen Hexagonen)
        if self.hex_size * self.zoom_factor > 20:
            self.canvas.create_text(
                screen_x, screen_y,
                text=f"{hex_x},{hex_y}",
                fill="black",
                font=("Arial", 8)
            )
    
    def _render_debug_info(self):
        """Rendert Debug-Informationen"""
        info_text = f"Zoom: {self.zoom_factor:.2f} | Hex Size: {self.hex_size:.1f} | View: ({self.view_x:.1f}, {self.view_y:.1f})"
        self.canvas.create_text(
            10, 10,
            text=info_text,
            fill="white",
            anchor="nw",
            font=("Arial", 9)
        )
    
    def reset_view(self):
        """Setzt die Ansicht zurück"""
        self.view_x = 0.0
        self.view_y = 0.0
        self.zoom_factor = 1.0
        self.hex_size = 15.0
        self.render_map()
    
    def center_on_grid(self):
        """Zentriert die Ansicht auf das Grid"""
        # Grid-Mittelpunkt berechnen
        grid_center_x = self.grid_manager.grid.width / 2.0
        grid_center_y = self.grid_manager.grid.height / 2.0
        
        # Zu Pixel-Koordinaten
        world_center_x, world_center_y = HexMath.hex_to_pixel(grid_center_x, grid_center_y, self.hex_size)
        
        # Canvas-Größe
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # View auf Zentrum setzen
        self.view_x = world_center_x - (canvas_width / 2.0) / self.zoom_factor
        self.view_y = world_center_y - (canvas_height / 2.0) / self.zoom_factor
        
        self.render_map()
    
    def get_widget(self) -> tk.Canvas:
        """Gibt das Canvas-Widget zurück"""
        return self.canvas
    
    def set_paint_mode(self, enabled: bool):
        """Aktiviert oder deaktiviert Paint-Mode"""
        self.paint_mode = enabled
        if not enabled:
            self.is_painting = False
            self.last_painted_tile = None
    
    def set_selected_terrain(self, terrain):
        """Setzt das aktuell ausgewählte Terrain für das Paint-Tool"""
        self.selected_terrain = terrain
    
    def _paint_tile(self, tile: Tile):
        """Malt ein Tile mit dem ausgewählten Terrain"""
        if self.selected_terrain and tile.area != self.selected_terrain:
            # Setze das neue Terrain
            old_area = tile.area
            tile.area = self.selected_terrain
            
            # Callback für andere Komponenten
            if self.on_tile_paint:
                self.on_tile_paint(tile, old_area)
            
            # Einzelnes Hex neu zeichnen für sofortiges visuelles Feedback
            self._render_single_hex(tile.coordinates[0], tile.coordinates[1], tile)
    
    def _render_single_hex(self, hex_x: int, hex_y: int, tile: Tile):
        """Rendert ein einzelnes Hex ohne komplettes Re-Render"""
        # Lösche altes Hex
        self.canvas.delete(f"hex_{hex_x}_{hex_y}")
        
        # Zeichne neues Hex
        self._render_hex(hex_x, hex_y, tile)