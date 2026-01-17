"""
Main Window Layout und UI-Komponenten
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional

from data.models import get_default_areas, FactionType, StrategicRoleType
from ui.dialogs import GridSizeDialog


class MainWindow:
    """Hauptfenster Layout und UI-Komponenten"""
    
    def __init__(self, root: tk.Tk, grid_manager, map_canvas):
        self.root = root
        self.grid_manager = grid_manager
        self.map_canvas = map_canvas  # Kann None sein bei Initialisierung
        
        # State Variables
        self.paint_tool_active = tk.BooleanVar()
        self.selected_terrain_var = tk.StringVar()
        self.faction_paint_active = tk.BooleanVar()
        self.selected_faction_var = tk.StringVar()
        self.brush_size = tk.IntVar(value=1)
        
        # Callbacks
        self.on_new_grid: Optional[Callable] = None
        # Export callbacks
        self.on_export: Optional[Callable] = None
        self.on_load: Optional[Callable] = None
        
        # Tile editing
        self.selected_tile = None
        self.tile_editor_vars = {}
        self.tile_editor_widgets = {}
        
        # Canvas Frame referenz für später
        self.canvas_frame = None
        
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
    
    def _create_menu(self):
        """Erstellt die Menübar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Grid...", command=self._new_grid)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def _create_main_layout(self):
        """Erstellt das Hauptlayout"""
        # Main Frame Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Info Panel (links)
        info_frame = ttk.LabelFrame(main_frame, text="Tools", width=200)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)
        info_frame.pack_propagate(False)
        
        # Grid-Info
        self.grid_info_label = ttk.Label(
            info_frame,
            text=f"Grid: {self.grid_manager.grid.width}x{self.grid_manager.grid.height}\\n"
                 f"Total Tiles: {len(self.grid_manager.grid.tiles)}",
            anchor="nw",
            justify=tk.LEFT
        )
        self.grid_info_label.pack(padx=10, pady=10, anchor="nw")
        
        # Controls-Info
        self._create_controls_info(info_frame)
        
        # Tool Panels
        self._create_paint_tool_panel(info_frame)
        self._create_faction_tool_panel(info_frame)
        self._create_export_panel(info_frame)
        
        # Map Canvas (mitte)
        canvas_frame = ttk.LabelFrame(main_frame, text="Map View")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Canvas Frame für späteren Zugriff speichern
        self.canvas_frame = canvas_frame
        
        # Properties Panel (rechts)
        props_frame = ttk.LabelFrame(main_frame, text="Tile Properties", width=250)
        props_frame.pack(side=tk.RIGHT, fill=tk.Y)
        props_frame.pack_propagate(False)
        
        self._create_properties_panel(props_frame)
        self._create_tile_editor_panel(props_frame)
    
    def setup_map_canvas(self, map_canvas):
        """Setzt Map Canvas nach der Initialisierung"""
        self.map_canvas = map_canvas
        if self.canvas_frame and map_canvas:
            map_canvas.canvas.pack(fill=tk.BOTH, expand=True)
    
    def _create_controls_info(self, parent):
        """Erstellt Controls-Hilfe"""
        controls_text = (
            "Controls:\\n"
            "• Mouse Drag: Pan\\n"
            "• Mouse Wheel: Zoom\\n"
            "• WASD: Pan\\n"
            "• R: Reset View\\n"
            "\\nPaint Mode:\\n"
            "• Hold Left Mouse: Paint\\n"
            "• Select terrain below\\n"
            "• Adjust brush size\\n"
            "\\nFaction Mode:\\n"
            "• Hold Left Mouse: Paint\\n"
            "• Select faction below\\n"
            "• Adjust brush size"
        )
        controls_label = ttk.Label(
            parent,
            text=controls_text,
            anchor="nw",
            justify=tk.LEFT
        )
        controls_label.pack(padx=10, pady=(20, 10), anchor="nw")
    
    def _create_paint_tool_panel(self, parent):
        """Erstellt Paint-Tool Panel"""
        paint_frame = ttk.LabelFrame(parent, text="Paint Tool")
        paint_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Paint-Tool Toggle
        self.paint_checkbox = ttk.Checkbutton(
            paint_frame,
            text="Enable Paint Tool",
            variable=self.paint_tool_active,
            command=self._toggle_paint_tool
        )
        self.paint_checkbox.pack(anchor="w", padx=5, pady=5)
        
        # Terrain-Auswahl
        ttk.Label(paint_frame, text="Terrain:").pack(anchor="w", padx=5)
        
        self.terrain_combo = ttk.Combobox(
            paint_frame,
            textvariable=self.selected_terrain_var,
            state="readonly",
            width=15
        )
        
        # Fülle Terrain-Typen
        areas = get_default_areas()
        terrain_names = [area.id for area in areas]
        self.terrain_combo['values'] = terrain_names
        self.terrain_combo.pack(fill=tk.X, padx=5, pady=5)
        self.terrain_combo.bind('<<ComboboxSelected>>', self._on_terrain_selected)
        
        # Brush Size Control
        self._create_brush_size_control(paint_frame, "terrain")
    
    def _create_faction_tool_panel(self, parent):
        """Erstellt Faction-Tool Panel"""
        faction_frame = ttk.LabelFrame(parent, text="Faction Tool")
        faction_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Faction-Tool Toggle
        self.faction_checkbox = ttk.Checkbutton(
            faction_frame,
            text="Enable Faction Tool",
            variable=self.faction_paint_active,
            command=self._toggle_faction_tool
        )
        self.faction_checkbox.pack(anchor="w", padx=5, pady=5)
        
        # Faction-Auswahl
        ttk.Label(faction_frame, text="Faction:").pack(anchor="w", padx=5)
        
        self.faction_combo = ttk.Combobox(
            faction_frame,
            textvariable=self.selected_faction_var,
            state="readonly",
            width=15
        )
        
        # Fülle Faction-Typen
        faction_names = [faction.value for faction in FactionType]
        self.faction_combo['values'] = faction_names
        self.faction_combo.pack(fill=tk.X, padx=5, pady=5)
        self.faction_combo.bind('<<ComboboxSelected>>', self._on_faction_selected)
        
        # Brush Size Control für Faction
        self._create_brush_size_control(faction_frame, "faction")
    
    def _create_brush_size_control(self, parent, prefix):
        """Erstellt Brush Size Kontrolle"""
        brush_size_frame = ttk.Frame(parent)
        brush_size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(brush_size_frame, text="Brush Size:").pack(side=tk.LEFT)
        
        brush_size_scale = ttk.Scale(
            brush_size_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.brush_size,
            command=self._on_brush_size_changed
        )
        brush_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        brush_size_label = ttk.Label(brush_size_frame, text="1")
        brush_size_label.pack(side=tk.RIGHT)
        
        # Labels speichern für Updates
        if prefix == "terrain":
            self.brush_size_label = brush_size_label
        else:
            self.faction_brush_size_label = brush_size_label
    
    def _create_export_panel(self, parent):
        """Erstellt Export Panel"""
        export_frame = ttk.LabelFrame(parent, text="Export")
        export_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.export_button = ttk.Button(
            export_frame,
            text="Export to JSON",
            command=lambda: self.on_export() if self.on_export else None
        )
        self.export_button.pack(fill=tk.X, padx=5, pady=5)
        
        self.load_button = ttk.Button(
            export_frame,
            text="Load from JSON",
            command=lambda: self.on_load() if self.on_load else None
        )
        self.load_button.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_properties_panel(self, parent):
        """Erstellt Properties Panel"""
        props_text_frame = ttk.Frame(parent)
        props_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text Widget mit Scrollbar
        self.props_text = tk.Text(
            props_text_frame,
            wrap=tk.WORD,
            width=30,
            height=10,
            state=tk.DISABLED
        )
        
        scrollbar = ttk.Scrollbar(props_text_frame, orient=tk.VERTICAL, command=self.props_text.yview)
        self.props_text.configure(yscrollcommand=scrollbar.set)
        
        self.props_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_tile_editor_panel(self, parent):
        """Erstellt das Tile-Editor Panel"""
        editor_frame = ttk.LabelFrame(parent, text="Edit Selected Tile")
        editor_frame.pack(fill=tk.X, padx=5, pady=(10, 0))
        
        # Info Label
        self.tile_info_label = ttk.Label(
            editor_frame,
            text="Click on a tile to edit its properties",
            anchor="center",
            justify=tk.CENTER
        )
        self.tile_info_label.pack(padx=5, pady=5)
        
        # Editor-Container (wird versteckt bis ein Tile ausgewählt ist)
        self.tile_editor_container = ttk.Frame(editor_frame)
        
        # Area/Terrain Dropdown
        area_frame = ttk.Frame(self.tile_editor_container)
        area_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(area_frame, text="Terrain:", width=12).pack(side=tk.LEFT)
        
        self.tile_editor_vars['area'] = tk.StringVar()
        area_combo = ttk.Combobox(
            area_frame,
            textvariable=self.tile_editor_vars['area'],
            state="readonly",
            width=12
        )
        areas = get_default_areas()
        area_combo['values'] = [area.display_name for area in areas]
        area_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        area_combo.bind('<<ComboboxSelected>>', self._on_tile_area_changed)
        self.tile_editor_widgets['area'] = area_combo
        
        # Is Land Checkbox
        land_frame = ttk.Frame(self.tile_editor_container)
        land_frame.pack(fill=tk.X, padx=5, pady=2)
        self.tile_editor_vars['is_land'] = tk.BooleanVar()
        land_check = ttk.Checkbutton(
            land_frame,
            text="Is Land",
            variable=self.tile_editor_vars['is_land'],
            command=self._on_tile_is_land_changed
        )
        land_check.pack(side=tk.LEFT)
        self.tile_editor_widgets['is_land'] = land_check
        
        # Faction Dropdown
        faction_frame = ttk.Frame(self.tile_editor_container)
        faction_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(faction_frame, text="Faction:", width=12).pack(side=tk.LEFT)
        
        self.tile_editor_vars['faction'] = tk.StringVar()
        faction_combo = ttk.Combobox(
            faction_frame,
            textvariable=self.tile_editor_vars['faction'],
            state="readonly",
            width=12
        )
        faction_combo['values'] = [faction.value for faction in FactionType]
        faction_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        faction_combo.bind('<<ComboboxSelected>>', self._on_tile_faction_changed)
        self.tile_editor_widgets['faction'] = faction_combo
        
        # Strategic Role Dropdown
        role_frame = ttk.Frame(self.tile_editor_container)
        role_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(role_frame, text="Strategic Role:", width=12).pack(side=tk.LEFT)
        
        self.tile_editor_vars['strategic_role'] = tk.StringVar()
        role_combo = ttk.Combobox(
            role_frame,
            textvariable=self.tile_editor_vars['strategic_role'],
            state="readonly",
            width=12
        )
        role_combo['values'] = [role.value for role in StrategicRoleType]
        role_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        role_combo.bind('<<ComboboxSelected>>', self._on_tile_strategic_role_changed)
        self.tile_editor_widgets['strategic_role'] = role_combo
        
        # Apply Button
        apply_frame = ttk.Frame(self.tile_editor_container)
        apply_frame.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        ttk.Button(
            apply_frame,
            text="Apply Changes",
            command=self._apply_tile_changes
        ).pack(fill=tk.X)
        
        # Container ist zu Beginn versteckt
        # self.tile_editor_container.pack() wird erst aufgerufen wenn ein Tile ausgewählt ist
    
    def _create_status_bar(self):
        """Erstellt die Statusleiste"""
        self.status_label = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _toggle_paint_tool(self):
        """Schaltet Paint-Tool an/aus"""
        is_active = self.paint_tool_active.get()
        if self.map_canvas:
            self.map_canvas.set_paint_mode(is_active)
        
        if is_active:
            self.faction_paint_active.set(False)
            if self.map_canvas:
                self.map_canvas.set_faction_paint_mode(False)
    
    def _toggle_faction_tool(self):
        """Schaltet Faction-Tool an/aus"""
        is_active = self.faction_paint_active.get()
        if self.map_canvas:
            self.map_canvas.set_faction_paint_mode(is_active)
        
        if is_active:
            self.paint_tool_active.set(False)
            if self.map_canvas:
                self.map_canvas.set_paint_mode(False)
    
    def _on_terrain_selected(self, event):
        """Terrain-Auswahl geändert"""
        terrain_name = self.selected_terrain_var.get()
        areas = get_default_areas()
        selected_terrain = next(
            (area for area in areas if area.id == terrain_name),
            areas[0] if areas else None
        )
        
        if selected_terrain:
            if self.map_canvas:
                self.map_canvas.set_selected_terrain(selected_terrain)
    
    def _on_faction_selected(self, event):
        """Faction-Auswahl geändert"""
        faction_name = self.selected_faction_var.get()
        faction = next(
            (f for f in FactionType if f.value == faction_name),
            FactionType.NEUTRAL
        )
        if self.map_canvas:
            self.map_canvas.set_selected_faction(faction)
    
    def _on_brush_size_changed(self, value):
        """Brush Size geändert"""
        brush_size = int(float(value))
        self.brush_size_label.config(text=str(brush_size))
        
        if hasattr(self, 'faction_brush_size_label'):
            self.faction_brush_size_label.config(text=str(brush_size))
        
        if self.map_canvas:
            self.map_canvas.set_brush_size(brush_size)
    
    def _new_grid(self):
        """Erstellt ein neues Grid"""
        if self.on_new_grid:
            self.on_new_grid()
    
    def update_grid_info(self):
        """Aktualisiert Grid-Info"""
        self.grid_info_label.config(
            text=f"Grid: {self.grid_manager.grid.width}x{self.grid_manager.grid.height}\\n"
                 f"Total Tiles: {len(self.grid_manager.grid.tiles)}"
        )
    
    def update_properties(self, text: str):
        """Aktualisiert Properties Panel"""
        self.props_text.config(state=tk.NORMAL)
        self.props_text.delete(1.0, tk.END)
        self.props_text.insert(1.0, text)
        self.props_text.config(state=tk.DISABLED)
    
    def set_status(self, text: str):
        """Setzt Statusleiste"""
        self.status_label.config(text=text)
    
    def post_init_setup(self):
        """Post-Initialisierung Setup"""
        # Initial Terrain und Faction setzen
        self._on_terrain_selected(None)
        self._on_faction_selected(None)
        self._on_brush_size_changed(1)
    
    def _on_tile_area_changed(self, event):
        """Area/Terrain für ausgewähltes Tile geändert"""
        if not self.selected_tile:
            return
        self._mark_tile_as_modified()
    
    def _on_tile_is_land_changed(self):
        """Is Land für ausgewähltes Tile geändert"""
        if not self.selected_tile:
            return
        self._mark_tile_as_modified()
    
    def _on_tile_faction_changed(self, event):
        """Faction für ausgewähltes Tile geändert"""
        if not self.selected_tile:
            return
        self._mark_tile_as_modified()
    
    def _on_tile_strategic_role_changed(self, event):
        """Strategic Role für ausgewähltes Tile geändert"""
        if not self.selected_tile:
            return
        self._mark_tile_as_modified()
    
    def _mark_tile_as_modified(self):
        """Markiert das Tile als modifiziert"""
        # Ändere Button-Text um anzuzeigen dass Änderungen vorliegen
        apply_button = None
        for child in self.tile_editor_container.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Button) and "Apply" in subchild.cget("text"):
                        apply_button = subchild
                        break
        
        if apply_button:
            apply_button.config(text="Apply Changes*")
    
    def _apply_tile_changes(self):
        """Wendet die Änderungen auf das ausgewählte Tile an"""
        if not self.selected_tile:
            return
        
        # Area/Terrain ändern
        area_name = self.tile_editor_vars['area'].get()
        areas = get_default_areas()
        selected_area = next(
            (area for area in areas if area.display_name == area_name),
            None
        )
        if selected_area:
            self.selected_tile.area = selected_area
        
        # Is Land ändern
        self.selected_tile.is_land = self.tile_editor_vars['is_land'].get()
        
        # Faction ändern
        faction_name = self.tile_editor_vars['faction'].get()
        faction = next(
            (f for f in FactionType if f.value == faction_name),
            FactionType.NEUTRAL
        )
        self.selected_tile.faction = faction
        
        # Strategic Role ändern
        role_name = self.tile_editor_vars['strategic_role'].get()
        role = next(
            (r for r in StrategicRoleType if r.value == role_name),
            StrategicRoleType.NONE
        )
        self.selected_tile.strategic_role = role
        
        # Karte neu rendern
        if self.map_canvas:
            self.map_canvas.render_map()
        
        # Button-Text zurücksetzen
        apply_button = None
        for child in self.tile_editor_container.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Button):
                        apply_button = subchild
                        break
        
        if apply_button:
            apply_button.config(text="Apply Changes")
        
        # Properties Text aktualisieren
        properties_text = self._format_tile_properties(self.selected_tile)
        self.update_properties(properties_text)
        
        # Status aktualisieren
        coords = self.selected_tile.coordinates
        self.set_status(f"Applied changes to tile at ({coords[0]}, {coords[1]})")
    
    def select_tile_for_editing(self, tile):
        """Wählt ein Tile für die Bearbeitung aus"""
        self.selected_tile = tile
        
        if tile:
            # Tile-Infos anzeigen
            coords = tile.coordinates
            self.tile_info_label.config(text=f"Editing Tile ({coords[0]}, {coords[1]})")
            
            # Editor-Container anzeigen
            if not self.tile_editor_container.winfo_manager():
                self.tile_editor_container.pack(fill=tk.X, padx=5, pady=5)
            
            # Aktuelle Werte in die Editor-Felder setzen
            if tile.area:
                self.tile_editor_vars['area'].set(tile.area.display_name)
            else:
                self.tile_editor_vars['area'].set("")
            
            self.tile_editor_vars['is_land'].set(tile.is_land)
            self.tile_editor_vars['faction'].set(tile.faction.value)
            self.tile_editor_vars['strategic_role'].set(tile.strategic_role.value)
        else:
            # Kein Tile ausgewählt
            self.tile_info_label.config(text="Click on a tile to edit its properties")
            
            # Editor-Container verstecken
            if self.tile_editor_container.winfo_manager():
                self.tile_editor_container.pack_forget()
    
    def _format_tile_properties(self, tile) -> str:
        """Formatiert Tile-Eigenschaften für Anzeige"""
        lines = []
        lines.append("=== TILE PROPERTIES ===")
        lines.append(f"Coordinates: {tile.coordinates}")
        lines.append("")
        
        if tile.area:
            lines.append("TERRAIN:")
            lines.append(f"  Type: {tile.area.display_name}")
            lines.append(f"  ID: {tile.area.id}")
            lines.append("")
        
        lines.append("PROPERTIES:")
        lines.append(f"  Is Land: {tile.is_land}")
        lines.append(f"  Faction: {tile.faction.value}")
        lines.append(f"  Strategic Role: {tile.strategic_role.value}")
        
        return "\\n".join(lines)