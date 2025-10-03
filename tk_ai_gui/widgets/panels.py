from __future__ import annotations
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from typing import Optional
from PIL import Image, ImageTk
from ..utils.ui import ToolTip


# Results table (labels/scores)

class ResultTable(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Treeview with 2 columns: "label" and "score" (no row headings)
        self.tree = ttk.Treeview(self, columns=("label", "score"), show="headings", height=6)
        self.tree.heading("label", text="Label")
        self.tree.heading("score", text="Score")
        self.tree.column("label", width=220, anchor="w")
        self.tree.column("score", width=80, anchor="center")

        # Always pair a Treeview with a Scrollbar; use yscrollcommand (not 'yscroll')
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)  # FIX: was yscroll=vsb.set (has no effect)

        # Grid placement + expand to fill
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def load(self, rows: list[dict]):
        """Replace table contents with up to the top 10 rows."""
        # Clear old rows first (prevents duplicates)
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insert with defensive defaults and score formatting
        for r in rows[:10]:
            label = r.get("label", "?")
            # float() cast protects against strings/None; .2f clamps presentation only
            score = f"{float(r.get('score', 0.0)):.2f}"
            self.tree.insert("", "end", values=(label, score))


# Input section (text/image, run buttons, CV2 toggle)

class InputPanel:
    def __init__(self, master, on_run1, on_run2, on_clear, on_browse):
        # Wrap in a labeled frame for visual grouping
        self.frame = ttk.LabelFrame(master, text="User Input", style="Section.TLabelframe")

        # Top row: input type selector + browse + preprocess toggle
        top = ttk.Frame(self.frame); top.pack(fill=tk.X, padx=8, pady=(8, 6))

        ttk.Label(top, text="Input Type:").pack(side=tk.LEFT)

        # "Text" or "Image" — you can switch model paths based on this
        self.input_var = tk.StringVar(value="Text")
        self.input_combo = ttk.Combobox(
            top, state="readonly", values=["Text", "Image"],
            textvariable=self.input_var, width=10
        )
        self.input_combo.pack(side=tk.LEFT, padx=(4, 8))
        ToolTip(self.input_combo, "Select input type (Text or Image)")

        # Image picker delegates to controller via callback
        b_browse = ttk.Button(top, text="Browse Image", command=on_browse)
        b_browse.pack(side=tk.LEFT)
        ToolTip(b_browse, "Choose an image file to classify")

        # Optional OpenCV preprocessing flag (consumed by controller)
        self.use_cv2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="OpenCV preprocess", variable=self.use_cv2)\
            .pack(side=tk.LEFT, padx=(8, 0))

        # Main text area for sentiment input (with built-in scrollbar)
        self.text_area = scrolledtext.ScrolledText(self.frame, height=7, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))

        # Live char/word counter; updated on key release
        self._counter = ttk.Label(self.frame, text="0 chars • 0 words", anchor="e")
        self._counter.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.text_area.bind("<KeyRelease>", self._update_counter)

        # Action buttons: callbacks are injected (keeps UI decoupled from models)
        btns = ttk.Frame(self.frame); btns.pack(fill=tk.X, padx=8, pady=(0, 10))
        b1 = ttk.Button(btns, text="Run Sentiment", command=on_run1, style="Accent.TButton")
        b2 = ttk.Button(btns, text="Run Image Classifier", command=on_run2)
        b3 = ttk.Button(btns, text="Clear", command=on_clear)
        b1.pack(side=tk.LEFT); b2.pack(side=tk.LEFT, padx=6); b3.pack(side=tk.LEFT, padx=6)

        # Context menu on right-click (Windows/Linux). Consider also Control-Click for macOS.
        self._menu = tk.Menu(self.frame, tearoff=0)
        self._menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self._menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self._menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.text_area.bind("<Button-3>", self._popup)

    def _popup(self, e):
        """Show right-click context menu at cursor position."""
        try:
            self._menu.tk_popup(e.x_root, e.y_root)
        finally:
            self._menu.grab_release()

    def _update_counter(self, _):
        """Compute live char/word counts; inexpensive for typical input sizes."""
        txt = self.text_area.get("1.0", "end").strip()
        words = len(txt.split()) if txt else 0
        self._counter.configure(text=f"{len(txt)} chars • {words} words")



# Output section (table + raw JSON view + copy/save)

class OutputPanel:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Results", style="Section.TLabelframe")

        # Title row
        top = ttk.Frame(self.frame); top.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(top, text="Summary", style="Title.TLabel").pack(side=tk.LEFT)

        # Summary table (labels/scores)
        self.table = ResultTable(self.frame)
        self.table.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        # Raw output view: pretty-printed JSON for debugging/export
        raw_box = ttk.LabelFrame(self.frame, text="Raw Output (JSON-like)", style="Section.TLabelframe")
        raw_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.output_text = scrolledtext.ScrolledText(raw_box, height=8, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Footer actions
        footer = ttk.Frame(self.frame); footer.pack(fill=tk.X, padx=8, pady=(0, 10))
        self.copy_btn = ttk.Button(footer, text="Copy to Clipboard", command=self.copy)
        self.save_btn = ttk.Button(footer, text="Save As…", command=self.save)
        self.copy_btn.pack(side=tk.LEFT); self.save_btn.pack(side=tk.LEFT, padx=6)

    def copy(self):
        """Copy raw JSON text to the OS clipboard."""
        txt = self.output_text.get("1.0", "end")
        self.frame.clipboard_clear()
        self.frame.clipboard_append(txt)

    def save(self):
        """Save raw JSON text to disk (UTF-8)."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            initialfile="result.json",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.output_text.get("1.0", "end"))

    def render(self, rows: list[dict]):
        """Populate the table and raw view from a list of {label, score} dicts."""
        self.table.load(rows)
        import json
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", json.dumps(rows, indent=2))



# Info section (model notes + OOP concepts)

class InfoPanel:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Model Information & OOP Notes", style="Section.TLabelframe")

        # Top box: dynamic model info (you can inject strings from controller)
        self.model_info = scrolledtext.ScrolledText(self.frame, height=8, wrap=tk.WORD)
        self.model_info.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 6))

        # Bottom box: static OOP notes; set to read-only after insert
        self.oop_info = scrolledtext.ScrolledText(self.frame, height=8, wrap=tk.WORD)
        self.oop_info.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.oop_info.insert(
            "1.0",
            "• Multiple inheritance: models inherit SaveLoadMixin + AIModelBase\n"
            "• Encapsulation: private __pipeline, protected _model_id\n"
            "• Polymorphism & overriding: models implement run() and info()\n"
            "• Multiple decorators: @log_call and @time_call on run(); error_handler on UI actions\n"
        )
        self.oop_info.configure(state="disabled")



# Simple image state holder (path + PIL image + Tk thumbnail)

class ImageState:
    def __init__(self):
        self.path: Optional[str] = None
        self.image: Optional[Image.Image] = None
        self.thumb: Optional[ImageTk.PhotoImage] = None  # Keep a reference or Tk will garbage-collect it



# Preview pane (thumbnail rendering)

class OutputPreview:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Preview", style="Section.TLabelframe")
        self.label = ttk.Label(self.frame, text="(no image)")
        self.label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def show_image(self, pil_img):
        """Show a scaled-down preview; keep self.thumb alive to avoid blank labels."""
        img = pil_img.copy()
        img.thumbnail((420, 300))  # Preserves aspect ratio within bounds
        self.thumb = ImageTk.PhotoImage(img)
        self.label.configure(image=self.thumb, text="")
