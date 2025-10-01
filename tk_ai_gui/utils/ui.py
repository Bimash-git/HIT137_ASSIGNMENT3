from __future__ import annotations
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(self.root)  # Style object controls widget looks
        self._bootstrap = None  # Will hold ttkbootstrap if available
        try:
            # Try to use ttkbootstrap (a modern theming library)
            import ttkbootstrap as tb  # type: ignore
            self._bootstrap = tb
            self.style.theme_use("cosmo") # Default bootstrap theme
        except Exception:
            # If ttkbootstrap not available, fall back to built-in ttk themes
            avail = self.style.theme_names()
            self.style.theme_use("clam" if "clam" in avail else avail[0])
        
        # Apply default font and styles    
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    # Method to change theme at runtime
    def set_theme(self, name: str):
        if self._bootstrap:
            try: self.style.theme_use(name); return
            except Exception: pass
            # Use built-in ttk theme if available
        if name in self.style.theme_names(): self.style.theme_use(name)

        # Get a list of available themes
    def available_themes(self) -> list[str]:
        if self._bootstrap:
            # Predefined bootstrap themes
            return ["cosmo","flatly","journal","litera","minty","pulse","sandstone","solar","united","yeti","darkly","cyborg","superhero","vapor"]
        # Otherwise return built-in ttk themes
        return list(self.style.theme_names())

class ToolTip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 300):
        # widget: the Tkinter widget to attach tooltip to
        #   text: tooltip text
        # delay: delay in ms before showing tooltip
        self.widget = widget; self.text = text; self.delay = delay
        self._id = None; self._tip = None

        # Bind mouse events
        self.widget.bind("<Enter>", self._on_enter) # Mouse enters widget
        self.widget.bind("<Leave>", self._on_leave) # Mouse leaves widget
        self.widget.bind("<ButtonPress>", self._on_leave) # Hide when clicked
        
        # When mouse enters → schedule tooltip
    def _on_enter(self, _): self._schedule()

    # When mouse leaves → cancel and hide tooltip
    def _on_leave(self, _): self._unschedule(); self._hide()

      # Schedule tooltip display after delay
    def _schedule(self):
        self._unschedule(); self._id = self.widget.after(self.delay, self._show)# Cancel previous schedule

        # Cancel scheduled tooltip if exists
    def _unschedule(self):
        if self._id: self.widget.after_cancel(self._id); self._id = None

        # Create and show tooltip window
    def _show(self):
        if self._tip or not self.text: return

           # Position tooltip near widget
        x, y, cx, cy = self.widget.bbox("insert") or (0,0,0,0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + cy + 20

         # Create a small floating window
        self._tip = tk.Toplevel(self.widget); self._tip.overrideredirect(True) # No window decorations
        self._tip.wm_attributes("-topmost", True) # Keep above all
        lbl = ttk.Label(self._tip, text=self.text, relief="solid", padding=(8,4))
        lbl.pack(); self._tip.geometry(f"+{x}+{y}") # Place tooltip at calculated position

        # Destroy tooltip window
    def _hide(self):
        if self._tip: self._tip.destroy(); self._tip = None
