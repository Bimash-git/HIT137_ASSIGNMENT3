from __future__ import annotations
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from typing import Optional
from PIL import Image, ImageTk
from ..utils.ui import ToolTip

class ResultTable(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.tree = ttk.Treeview(self, columns=("label", "score"), show="headings", height=6)
        self.tree.heading("label", text="Label")
        self.tree.heading("score", text="Score")
        self.tree.column("label", width=220, anchor="w")
        self.tree.column("score", width=80, anchor="center")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    def load(self, rows: list[dict]):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in rows[:10]:
            self.tree.insert("", "end", values=(r.get("label","?"), f"{float(r.get('score',0.0)):.2f}"))

class InputPanel:
    def __init__(self, master, on_run1, on_run2, on_clear, on_browse):
        self.frame = ttk.LabelFrame(master, text="User Input", style="Section.TLabelframe")
        top = ttk.Frame(self.frame); top.pack(fill=tk.X, padx=8, pady=(8,6))
        ttk.Label(top, text="Input Type:").pack(side=tk.LEFT)
        self.input_var = tk.StringVar(value="Text")
        self.input_combo = ttk.Combobox(top, state="readonly", values=["Text", "Image"], textvariable=self.input_var, width=10)
        self.input_combo.pack(side=tk.LEFT, padx=(4,8))
        ToolTip(self.input_combo, "Select input type (Text or Image)")
        b_browse = ttk.Button(top, text="Browse Image", command=on_browse); b_browse.pack(side=tk.LEFT)
        ToolTip(b_browse, "Choose an image file to classify")
        self.use_cv2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="OpenCV preprocess", variable=self.use_cv2).pack(side=tk.LEFT, padx=(8,0))
        self.text_area = scrolledtext.ScrolledText(self.frame, height=7, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,6))
        self._counter = ttk.Label(self.frame, text="0 chars • 0 words", anchor="e")
        self._counter.pack(fill=tk.X, padx=8, pady=(0,6))
        self.text_area.bind("<KeyRelease>", self._update_counter)
        btns = ttk.Frame(self.frame); btns.pack(fill=tk.X, padx=8, pady=(0,10))
        b1 = ttk.Button(btns, text="Run Sentiment", command=on_run1, style="Accent.TButton")
        b2 = ttk.Button(btns, text="Run Image Classifier", command=on_run2)
        b3 = ttk.Button(btns, text="Clear", command=on_clear)
        b1.pack(side=tk.LEFT); b2.pack(side=tk.LEFT, padx=6); b3.pack(side=tk.LEFT, padx=6)
        self._menu = tk.Menu(self.frame, tearoff=0)
        self._menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self._menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self._menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.text_area.bind("<Button-3>", self._popup)
    def _popup(self, e):
        try: self._menu.tk_popup(e.x_root, e.y_root)
        finally: self._menu.grab_release()
    def _update_counter(self, _):
        txt = self.text_area.get("1.0", "end").strip()
        words = len(txt.split()) if txt else 0
        self._counter.configure(text=f"{len(txt)} chars • {words} words")

class OutputPanel:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Results", style="Section.TLabelframe")
        top = ttk.Frame(self.frame); top.pack(fill=tk.X, padx=8, pady=(8,0))
        ttk.Label(top, text="Summary", style="Title.TLabel").pack(side=tk.LEFT)
        self.table = ResultTable(self.frame); self.table.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4,8))
        raw_box = ttk.LabelFrame(self.frame, text="Raw Output (JSON-like)", style="Section.TLabelframe")
        raw_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))
        self.output_text = scrolledtext.ScrolledText(raw_box, height=8, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        footer = ttk.Frame(self.frame); footer.pack(fill=tk.X, padx=8, pady=(0,10))
        self.copy_btn = ttk.Button(footer, text="Copy to Clipboard", command=self.copy)
        self.save_btn = ttk.Button(footer, text="Save As…", command=self.save)
        self.copy_btn.pack(side=tk.LEFT); self.save_btn.pack(side=tk.LEFT, padx=6)
    def copy(self):
        txt = self.output_text.get("1.0", "end")
        self.frame.clipboard_clear(); self.frame.clipboard_append(txt)
    def save(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json"),("All files","*.*")], initialfile="result.json")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: f.write(self.output_text.get("1.0", "end"))
    def render(self, rows: list[dict]):
        self.table.load(rows)
        import json
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", json.dumps(rows, indent=2))

class InfoPanel:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Model Information & OOP Notes", style="Section.TLabelframe")
        self.model_info = scrolledtext.ScrolledText(self.frame, height=8, wrap=tk.WORD)
        self.model_info.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8,6))
        self.oop_info = scrolledtext.ScrolledText(self.frame, height=8, wrap=tk.WORD)
        self.oop_info.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))
        self.oop_info.insert("1.0",
            "• Multiple inheritance: models inherit SaveLoadMixin + AIModelBase\n"
            "• Encapsulation: private __pipeline, protected _model_id\n"
            "• Polymorphism & overriding: models implement run() and info()\n"
            "• Multiple decorators: @log_call and @time_call on run(); error_handler on UI actions\n"
        )
        self.oop_info.configure(state="disabled")

class ImageState:
    def __init__(self):
        self.path: Optional[str] = None
        self.image: Optional[Image.Image] = None
        self.thumb: Optional[ImageTk.PhotoImage] = None

class OutputPreview:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Preview", style="Section.TLabelframe")
        self.label = ttk.Label(self.frame, text="(no image)")
        self.label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    def show_image(self, pil_img):
        img = pil_img.copy(); img.thumbnail((420, 300))
        self.thumb = ImageTk.PhotoImage(img); self.label.configure(image=self.thumb, text="")
