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
            "• Click: Select Tile"
        )
        controls_label = ttk.Label(
            info_frame,
            text=controls_text,
            anchor="nw",
            justify=tk.LEFT
        )
        controls_label.pack(padx=10, pady=(20, 10), anchor="nw")
        
        # Map Canvas (rechts)
        canvas_frame = ttk.LabelFrame(main_frame, text="Map View")
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Map Canvas erstellen
        self.map_canvas = MapCanvas(canvas_frame, self.grid_manager)
        self.map_canvas.get_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Callbacks setzen
        self.map_canvas.on_tile_hover = self._on_tile_hover
        self.map_canvas.on_tile_click = self._on_tile_click
        
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
• Linke Maustaste + Ziehen: Karte bewegen (Pan)
• Mausrad: Zoomen
• Linke Maustaste: Tile auswählen

Tastatur:
• W, A, S, D: Karte bewegen
• R: Ansicht zurücksetzen

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