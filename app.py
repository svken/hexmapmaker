"""
Hauptanwendungs-Controller
Koordiniert alle Komponenten
"""
import tkinter as tk
from data.grid_manager import GridManager
from ui.map_canvas import MapCanvas
from ui.main_window import MainWindow
from ui.event_handlers import EventHandlers
from ui.dialogs import GridSizeDialog
from export.godot_exporter import MapExporter


class HexMapApplication:
    """Hauptanwendungs-Controller für den Hex Map Editor"""
    
    def __init__(self):
        """Initialisiert die Anwendung"""
        # Hauptfenster
        self.root = tk.Tk()
        self.root.title("Hex Map Editor - Idle War")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Core-Komponenten
        self.grid_manager = GridManager()
        self.map_canvas = None
        self.main_window = None
        self.event_handlers = None
        self.exporter = None  # Wird nach Canvas-Erstellung initialisiert
        
        self._initialize_components()
        self._setup_callbacks()
        
        # Post-Init Setup
        self.root.after(200, self._post_init_setup)
    
    def _initialize_components(self):
        """Initialisiert alle UI-Komponenten"""        
        # Main Window erstellen (erstellt das Layout)
        self.main_window = MainWindow(self.root, self.grid_manager, None)
        
        # Map Canvas mit dem Canvas-Frame erstellen
        if self.main_window.canvas_frame:
            self.map_canvas = MapCanvas(self.main_window.canvas_frame, self.grid_manager)
            
            # Canvas in Main Window einbetten
            self.main_window.setup_map_canvas(self.map_canvas)
            
            # Event Handlers erstellen
            self.event_handlers = EventHandlers(
                self.main_window, 
                self.grid_manager, 
                self.map_canvas
            )
            
            # Exporter mit Canvas-Referenz erstellen
            self.exporter = MapExporter(self.grid_manager, self.map_canvas)
    
    def _setup_callbacks(self):
        """Setzt Callbacks zwischen Komponenten"""
        self.main_window.on_new_grid = self._create_new_grid
        self.main_window.on_export = self._export_map
        self.main_window.on_load = self._load_map
    
    def _post_init_setup(self):
        """Post-Initialisierung Setup"""
        # Map Canvas initial rendern
        self.map_canvas.render_map()
        
        # Main Window Setup
        self.main_window.post_init_setup()
        
        # Focus auf Canvas setzen
        self.map_canvas.canvas.focus_set()
    
    def _create_new_grid(self):
        """Erstellt ein neues Grid"""
        current_grid = self.grid_manager.grid
        dialog = GridSizeDialog(
            self.root, 
            current_grid.width, 
            current_grid.height
        )
        result = dialog.show()
        
        if result:
            width, height = result
            
            # Neues Grid erstellen
            self.grid_manager.create_new_grid(width, height)
            
            # UI aktualisieren
            self.main_window.update_grid_info()
            
            # Map neu rendern
            self.map_canvas.render_map()
            
            self.main_window.set_status(f"Created new grid: {width}x{height}")
    
    def _export_map(self):
        """Exportiert die Karte"""
        success = self.exporter.export_map()
        if success:
            self.main_window.set_status("Map exported successfully")
    
    def _load_map(self):
        """Lädt eine Karte aus JSON"""
        success = self.exporter.load_map()
        if success:
            # UI aktualisieren
            self.main_window.update_grid_info()
            
            # Map neu rendern
            self.map_canvas.render_map()
            
            self.main_window.set_status("Map loaded successfully")
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()


if __name__ == "__main__":
    app = HexMapApplication()
    app.run()