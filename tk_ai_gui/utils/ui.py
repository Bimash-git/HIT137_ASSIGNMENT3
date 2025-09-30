from __future__ import annotations
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(self.root)
        self._bootstrap = None
        try:
            import ttkbootstrap as tb  # type: ignore
            self._bootstrap = tb
            self.style.theme_use("cosmo")
        except Exception:
            avail = self.style.theme_names()
            self.style.theme_use("clam" if "clam" in avail else avail[0])
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def set_theme(self, name: str):
        if self._bootstrap:
            try: self.style.theme_use(name); return
            except Exception: pass
        if name in self.style.theme_names(): self.style.theme_use(name)

    def available_themes(self) -> list[str]:
        if self._bootstrap:
            return ["cosmo","flatly","journal","litera","minty","pulse","sandstone","solar","united","yeti","darkly","cyborg","superhero","vapor"]
        return list(self.style.theme_names())

class ToolTip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 300):
        self.widget = widget; self.text = text; self.delay = delay
        self._id = None; self._tip = None
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)
    def _on_enter(self, _): self._schedule()
    def _on_leave(self, _): self._unschedule(); self._hide()
    def _schedule(self):
        self._unschedule(); self._id = self.widget.after(self.delay, self._show)
    def _unschedule(self):
        if self._id: self.widget.after_cancel(self._id); self._id = None
    def _show(self):
        if self._tip or not self.text: return
        x, y, cx, cy = self.widget.bbox("insert") or (0,0,0,0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + cy + 20
        self._tip = tk.Toplevel(self.widget); self._tip.overrideredirect(True)
        self._tip.wm_attributes("-topmost", True)
        lbl = ttk.Label(self._tip, text=self.text, relief="solid", padding=(8,4))
        lbl.pack(); self._tip.geometry(f"+{x}+{y}")
    def _hide(self):
        if self._tip: self._tip.destroy(); self._tip = None
