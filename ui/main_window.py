"""
Main Window Layout und UI-Komponenten
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional

from data.models import get_default_areas, FactionType
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
        self.on_export: Optional[Callable] = None
        
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
            text="Export to Godot (.tres)",
            command=lambda: self.on_export() if self.on_export else None
        )
        self.export_button.pack(fill=tk.X, padx=5, pady=5)
    
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