"""
Hex Map Editor - Hauptanwendung
Einfache GUI mit Hex-Grid-Anzeige und Pan/Zoom-Funktionalität
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.models import Grid
from data.grid_manager import GridManager
from ui.map_canvas import MapCanvas


class HexMapEditor:
    """Haupt-Anwendung für den Hex Map Editor"""
    
    def __init__(self):
        """Initialisiert die Anwendung"""
        # Hauptfenster erstellen
        self.root = tk.Tk()
        self.root.title("Hex Map Editor - Idle War")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Grid Manager
        self.grid_manager = GridManager()
        
        # Paint-Tool State
        self.paint_tool_active = tk.BooleanVar()
        self.selected_terrain_var = tk.StringVar()
        
        # Faction-Paint-Tool State
        self.faction_paint_active = tk.BooleanVar()
        self.selected_faction_var = tk.StringVar()
        
        # Brush Size State
        self.brush_size = tk.IntVar(value=1)  # Standard: 1 Tile
        
        # GUI erstellen
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        
        # Nach dem Layout auf Grid zentrieren
        self.root.after(200, self._post_init_setup)
    
    def _create_menu(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Map...", command=self._new_map)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View-Menü
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset View", command=self._reset_view)
        view_menu.add_command(label="Center on Grid", command=self._center_on_grid)
        
        # Help-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Controls", command=self._show_controls)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Erstellt das Haupt-Layout"""
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Info-Panel (links)
        info_frame = ttk.LabelFrame(main_frame, text="Map Info", width=200)
        info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        info_frame.pack_propagate(False)
        
        # Grid-Info
        self.grid_info_label = ttk.Label(
            info_frame, 
            text=f"Grid Size: {self.grid_manager.grid.width} x {self.grid_manager.grid.height}\\n"
                 f"Total Tiles: {len(self.grid_manager.grid.tiles)}",
            anchor="nw",
            justify=tk.LEFT
        )
        self.grid_info_label.pack(padx=10, pady=10, anchor="nw")
        
        # Controls-Info
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
            info_frame,
            text=controls_text,
            anchor="nw",
            justify=tk.LEFT
        )
        controls_label.pack(padx=10, pady=(20, 10), anchor="nw")
        
        # Paint-Tool Panel
        paint_frame = ttk.LabelFrame(info_frame, text="Paint Tool")
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
        ttk.Label(paint_frame, text="Terrain Type:").pack(anchor="w", padx=5)
        
        terrain_frame = ttk.Frame(paint_frame)
        terrain_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.terrain_combo = ttk.Combobox(
            terrain_frame,
            textvariable=self.selected_terrain_var,
            state="readonly",
            width=15
        )
        
        # Fülle Terrain-Typen
        terrain_names = [area.display_name for area in self.grid_manager.grid.area_definitions]
        self.terrain_combo['values'] = terrain_names
        if terrain_names:
            self.terrain_combo.set(terrain_names[1])  # Plain als Standard
            
        self.terrain_combo.pack(fill=tk.X)
        self.terrain_combo.bind('<<ComboboxSelected>>', self._on_terrain_selected)
        
        # Brush Size Control
        brush_size_frame = ttk.Frame(paint_frame)
        brush_size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(brush_size_frame, text="Brush Size:").pack(side=tk.LEFT)
        
        self.brush_size_scale = ttk.Scale(
            brush_size_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.brush_size,
            command=self._on_brush_size_changed
        )
        self.brush_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.brush_size_label = ttk.Label(brush_size_frame, text="1")
        self.brush_size_label.pack(side=tk.RIGHT)
        
        # Faction-Paint-Tool Panel
        faction_frame = ttk.LabelFrame(info_frame, text="Faction Tool")
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
        
        faction_combo_frame = ttk.Frame(faction_frame)
        faction_combo_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.faction_combo = ttk.Combobox(
            faction_combo_frame,
            textvariable=self.selected_faction_var,
            state="readonly",
            width=15
        )
        
        # Fülle Faction-Typen
        self.faction_combo['values'] = ["NEUTRAL", "BLUE", "RED"]
        self.faction_combo.set("BLUE")  # Blue als Standard
            
        self.faction_combo.pack(fill=tk.X)
        self.faction_combo.bind('<<ComboboxSelected>>', self._on_faction_selected)
        
        # Map Canvas (mitte)
        canvas_frame = ttk.LabelFrame(main_frame, text="Map View")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Properties Panel (rechts)
        props_frame = ttk.LabelFrame(main_frame, text="Tile Properties", width=250)
        props_frame.pack(side=tk.RIGHT, fill=tk.Y)
        props_frame.pack_propagate(False)
        
        # Scrollable Text Widget für Properties
        props_text_frame = ttk.Frame(props_frame)
        props_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text Widget mit Scrollbar
        self.props_text = tk.Text(
            props_text_frame,
            wrap=tk.WORD,
            width=30,
            height=20,
            font=("Courier", 9),
            bg="#f0f0f0",
            state=tk.DISABLED
        )
        
        props_scrollbar = ttk.Scrollbar(props_text_frame, orient=tk.VERTICAL, command=self.props_text.yview)
        self.props_text.config(yscrollcommand=props_scrollbar.set)
        
        self.props_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        props_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial Text
        self._update_properties_panel(None)
        
        # Map Canvas erstellen
        self.map_canvas = MapCanvas(canvas_frame, self.grid_manager)
        self.map_canvas.get_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Callbacks setzen
        self.map_canvas.on_tile_hover = self._on_tile_hover
        self.map_canvas.on_tile_click = self._on_tile_click
        self.map_canvas.on_tile_paint = self._on_tile_paint
        self.map_canvas.on_faction_paint = self._on_faction_paint
        
        # Initial Terrain und Faction setzen
        self._on_terrain_selected(None)
        self._on_faction_selected(None)
        self._on_brush_size_changed(1)
        
        # Focus für Keyboard-Input
        self.map_canvas.get_widget().focus_set()
    
    def _create_status_bar(self):
        """Erstellt die Status-Leiste"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        
        # Status-Text
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Koordinaten-Anzeige
        self.coords_label = ttk.Label(self.status_bar, text="")
        self.coords_label.pack(side=tk.RIGHT)
    
    def _new_map(self):
        """Erstellt eine neue Karte"""
        # Dialog für Grid-Größe
        dialog = NewMapDialog(self.root)
        if dialog.result:
            width, height = dialog.result
            self.grid_manager.create_new_grid(width, height)
            self.map_canvas.render_map()
            self.map_canvas.center_on_grid()
            
            # Info aktualisieren
            self.grid_info_label.config(
                text=f"Grid Size: {width} x {height}\\n"
                     f"Total Tiles: {width * height}"
            )
    
    def _show_controls(self):
        """Zeigt die Steuerungs-Hilfe"""
        controls_text = """
Steuerung:

Maus:
• Linke Maustaste + Ziehen: Karte bewegen (Pan) / Malen (Paint-Mode)
• Mausrad: Zoomen
• Linke Maustaste: Tile auswählen

Tastatur:
• W, A, S, D: Karte bewegen
• R: Ansicht zurücksetzen

Paint-Tool:
• Paint Tool aktivieren im linken Panel
• Terrain-Typ auswählen
• Linke Maustaste gedrückt halten und über Tiles bewegen zum Malen

Menü:
• File > New Map: Neue Karte erstellen
• View > Center on Grid: Auf Karte zentrieren
        """
        messagebox.showinfo("Controls", controls_text)
    
    def _show_about(self):
        """Zeigt About-Dialog"""
        about_text = """
Hex Map Editor für Idle War

Version: 1.0.0 (MVP)
Entwicklung: Phase 1 - Core Funktionalität

Features:
• Hex-Grid Darstellung
• Zoom und Pan
• Basis Grid-Verwaltung

Kommende Features:
• Terrain-Editing
• Godot-Export
• Layer-System
        """
        messagebox.showinfo("About Hex Map Editor", about_text)
    
    def _on_tile_hover(self, tile):
        """Wird aufgerufen wenn Maus über Tile ist"""
        if tile:
            coords_text = f"Hex: ({tile.coordinates[0]}, {tile.coordinates[1]})"
            if tile.area:
                coords_text += f" | {tile.area.display_name}"
        else:
            coords_text = ""
        
        self.coords_label.config(text=coords_text)
        
        # Update Properties Panel
        self._update_properties_panel(tile)
    
    def _on_tile_click(self, tile):
        """Wird aufgerufen wenn Tile geklickt wird"""
        # Alle Tiles deselektieren
        for t in self.grid_manager.get_all_tiles():
            t.is_selected = False
        
        # Aktuelles Tile selektieren
        tile.is_selected = True
        
        # Status aktualisieren
        self.status_label.config(
            text=f"Selected: Hex ({tile.coordinates[0]}, {tile.coordinates[1]})"
        )
        
        # Map neu rendern für Selektion
        self.map_canvas.render_map()
    
    def _post_init_setup(self):
        """Setup nach der GUI-Initialisierung"""
        try:
            self.map_canvas.center_on_grid()
        except Exception as e:
            print(f"Post-init setup error: {e}")
            # Nochmal versuchen
            self.root.after(200, self._post_init_setup)
    
    def _reset_view(self):
        """Wrapper für Reset View"""
        if hasattr(self, 'map_canvas'):
            self.map_canvas.reset_view()
    
    def _center_on_grid(self):
        """Wrapper für Center on Grid"""
        if hasattr(self, 'map_canvas'):
            self.map_canvas.center_on_grid()
    
    def _toggle_paint_tool(self):
        """Aktiviert/deaktiviert das Paint-Tool"""
        is_active = self.paint_tool_active.get()
        
        if hasattr(self, 'map_canvas'):
            self.map_canvas.set_paint_mode(is_active)
            
            # Status aktualisieren
            if is_active:
                terrain_name = self.selected_terrain_var.get()
                self.status_label.config(text=f"Paint Tool activated: {terrain_name} - Hold left mouse to paint")
                # Faction-Tool deaktivieren wenn Paint-Tool aktiviert wird
                if self.faction_paint_active.get():
                    self.faction_paint_active.set(False)
                    self.map_canvas.set_faction_paint_mode(False)
            else:
                self.status_label.config(text="Paint Tool deactivated")
    
    def _on_terrain_selected(self, event):
        """Wird aufgerufen wenn ein neuer Terrain-Typ ausgewählt wird"""
        selected_name = self.selected_terrain_var.get()
        
        # Finde das entsprechende Area-Objekt
        selected_area = None
        for area in self.grid_manager.grid.area_definitions:
            if area.display_name == selected_name:
                selected_area = area
                break
        
        if hasattr(self, 'map_canvas') and selected_area:
            self.map_canvas.set_selected_terrain(selected_area)
            
            if self.paint_tool_active.get():
                self.status_label.config(text=f"Paint Tool: {selected_name} selected")
    
    def _toggle_faction_tool(self):
        """Aktiviert/deaktiviert das Faction-Tool"""
        is_active = self.faction_paint_active.get()
        
        if hasattr(self, 'map_canvas'):
            self.map_canvas.set_faction_paint_mode(is_active)
            
            # Status aktualisieren
            if is_active:
                faction_name = self.selected_faction_var.get()
                self.status_label.config(text=f"Faction Tool activated: {faction_name} - Hold left mouse to paint")
                # Terrain-Tool deaktivieren wenn Faction-Tool aktiviert wird
                if self.paint_tool_active.get():
                    self.paint_tool_active.set(False)
                    self.map_canvas.set_paint_mode(False)
            else:
                self.status_label.config(text="Faction Tool deactivated")
    
    def _on_faction_selected(self, event):
        """Wird aufgerufen wenn eine neue Fraktion ausgewählt wird"""
        from data.models import FactionType
        
        selected_name = self.selected_faction_var.get()
        
        # Konvertiere String zu FactionType Enum
        selected_faction = None
        if selected_name == "NEUTRAL":
            selected_faction = FactionType.NEUTRAL
        elif selected_name == "BLUE":
            selected_faction = FactionType.BLUE
        elif selected_name == "RED":
            selected_faction = FactionType.RED
        
        if hasattr(self, 'map_canvas') and selected_faction:
            self.map_canvas.set_selected_faction(selected_faction)
            
            if self.faction_paint_active.get():
                self.status_label.config(text=f"Faction Tool: {selected_name} selected")
    
    def _on_faction_paint(self, tile, old_faction):
        """Wird aufgerufen wenn ein Tile mit Fraktion gemalt wird"""
        faction_name = tile.faction.value
        coords_text = f"Painted faction {faction_name} at ({tile.coordinates[0]}, {tile.coordinates[1]})"
        self.status_label.config(text=coords_text)
    
    def _on_brush_size_changed(self, value):
        """Wird aufgerufen wenn sich die Pinselgröße ändert"""
        brush_size = int(float(value))
        self.brush_size_label.config(text=str(brush_size))
        
        if hasattr(self, 'map_canvas'):
            self.map_canvas.set_brush_size(brush_size)
    
    def _on_tile_paint(self, tile, old_area):
        """Wird aufgerufen wenn ein Tile gemalt wird"""
        terrain_name = tile.area.display_name if tile.area else "Unknown"
        coords_text = f"Painted {terrain_name} at ({tile.coordinates[0]}, {tile.coordinates[1]})"
        self.status_label.config(text=coords_text)
    
    def _update_properties_panel(self, tile):
        """Aktualisiert das Properties Panel mit Tile-Informationen"""
        self.props_text.config(state=tk.NORMAL)
        self.props_text.delete(1.0, tk.END)
        
        if tile is None:
            self.props_text.insert(tk.END, "Hover over a tile to see its properties")
        else:
            # Formatiere alle Tile-Attribute
            props_text = f"""TILE PROPERTIES
{'=' * 30}

Coordinates: ({tile.coordinates[0]}, {tile.coordinates[1]})

TERRAIN:
Area: {tile.area.display_name if tile.area else 'None'}
Area ID: {tile.area.id if tile.area else 'None'}
Is Land: {tile.is_land}

TERRAIN STATS:
Move Cost: {tile.area.move_cost if tile.area else 'N/A'}
Attack Mult: {tile.area.attack_mult if tile.area else 'N/A'}
Defense Mult: {tile.area.defense_mult if tile.area else 'N/A'}

RESOURCES:
Resource Type: {tile.resource.value}
Resource Count: {tile.resource_count:.1f}
Regen Rate: {tile.resource_regeneration_rate:.2f}
Max Capacity: {tile.max_resource_capacity:.1f}

MILITARY:
Faction: {tile.faction.value}
In Battle: {tile.in_battle}
Front Degree: {tile.front_degree}
Strength: {tile.strength:.1f}
Fortification: {tile.fortification_level}
Garrison Size: {tile.garrison_size}

ENVIRONMENT:
Elevation: {tile.elevation:.1f}m
Temperature: {tile.temperature:.1f}°C
Fertility: {tile.fertility:.2f}
Accessibility: {tile.accessibility:.2f}

STRUCTURES:
Structures: {', '.join(tile.structures) if tile.structures else 'None'}
Population: {tile.population}
Happiness: {tile.happiness:.1f}%

STRATEGIC:
Strategic Value: {tile.strategic_value}
Supply Lines: {len(tile.supply_lines)}
Visibility: {tile.visibility}

UI:
Selected: {tile.is_selected}
Neighbors: {tile.neighbour_tiles}"""
            
            self.props_text.insert(tk.END, props_text)
        
        self.props_text.config(state=tk.DISABLED)
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()


class NewMapDialog:
    """Dialog für neue Karten-Erstellung"""
    
    def __init__(self, parent):
        self.result = None
        
        # Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Map")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentrieren
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        
        # Warten auf Schließung
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Erstellt Dialog-Widgets"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ttk.Label(main_frame, text="Create New Map", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Größen-Eingabe
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.width_var = tk.StringVar(value="50")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, sticky="w")
        
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        self.height_var = tk.StringVar(value="50")
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Create", command=self._create).pack(side=tk.RIGHT)
        
        # Enter-Key Binding
        self.dialog.bind('<Return>', lambda e: self._create())
        width_entry.focus()
    
    def _create(self):
        """Erstellt die neue Karte"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 10 or width > 200 or height < 10 or height > 200:
                messagebox.showerror("Error", "Size must be between 10 and 200")
                return
            
            self.result = (width, height)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def _cancel(self):
        """Bricht ab"""
        self.dialog.destroy()


if __name__ == "__main__":
    app = HexMapEditor()
    app.run()