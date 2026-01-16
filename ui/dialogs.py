"""
Dialog-Fenster für verschiedene UI-Interaktionen
"""
import tkinter as tk
from tkinter import ttk, messagebox


class GridSizeDialog:
    """Dialog für Grid-Größe Eingabe"""
    
    def __init__(self, parent, current_width=50, current_height=50):
        self.result = None
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Grid Size")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Variables
        self.width_var = tk.StringVar(value=str(current_width))
        self.height_var = tk.StringVar(value=str(current_height))
        
        self._create_widgets()
        
        # Enter/Escape bindings
        self.dialog.bind('<Return>', lambda e: self._ok())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # Focus auf width entry
        self.width_entry.focus()
    
    def _create_widgets(self):
        """Erstellt Dialog-Widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Enter new grid dimensions:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(pady=(0, 20))
        
        # Width
        width_frame = ttk.Frame(main_frame)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text="Width:", width=10).pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var)
        self.width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Height
        height_frame = ttk.Frame(main_frame)
        height_frame.pack(fill=tk.X, pady=5)
        ttk.Label(height_frame, text="Height:", width=10).pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var)
        self.height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Info
        info_text = "Size range: 10-200\\nLarge grids may be slow"
        ttk.Label(main_frame, text=info_text, 
                 font=('TkDefaultFont', 8)).pack(pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", 
                  command=self._ok).pack(side=tk.RIGHT)
    
    def _ok(self):
        """OK gedrückt"""
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
        """Cancel gedrückt"""
        self.dialog.destroy()
    
    def show(self):
        """Zeigt Dialog und wartet auf Ergebnis"""
        self.dialog.wait_window()
        return self.result