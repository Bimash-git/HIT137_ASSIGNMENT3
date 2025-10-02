from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, queue
from .controller import ModelManager
from .widgets.panels import InputPanel, OutputPanel, InfoPanel, ImageState, OutputPreview
from .utils.ui import ThemeManager, ToolTip
from .utils.decorators import error_handler
from .utils.imaging import preprocess_image_cv2

class MainWindow:
    def __init__(self, root):
        # create the main window for the app
        self.root = root
        self.root.title("AI Studio — Tkinter + Transformers + OpenCV (Final)")
        self.root.geometry("1140x740")

        # model manager will load and run ML models
        self.mm = ModelManager()

        # theme manager lets the user change color themes
        self.theme = ThemeManager(self.root)

        # background job queue for running models without freezing UI
        self._job_q: queue.Queue = queue.Queue()
        self._last_result = None
        self._busy = False
        self.root.after(75, self._poll_job_queue)  # check job queue every 100ms

        # ----- top bar with title, task selector, theme selector, and status -----
        top = ttk.Frame(self.root); top.pack(fill=tk.X, padx=10, pady=(10,6))
        ttk.Label(top, text="AI Model Studio", style="Title.TLabel").pack(side=tk.LEFT)

        # task dropdown (choose between text sentiment and image classification)
        ttk.Label(top, text="Task:", padding=(12,0)).pack(side=tk.LEFT)
        self.task_var = tk.StringVar(value="Text Sentiment")
        self.task_combo = ttk.Combobox(top, state="readonly",
            values=["Text Sentiment","Image Classification"],
            textvariable=self.task_var, width=20)
        self.task_combo.pack(side=tk.LEFT)
        self.task_combo.bind("<<ComboboxSelected>>", self._on_task_change)

        # theme dropdown (light, dark etc.)
        ttk.Label(top, text="Theme:", padding=(12,0)).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.theme.available_themes()[0])
        self.theme_combo = ttk.Combobox(top, state="readonly",
            values=self.theme.available_themes(),
            textvariable=self.theme_var, width=14)
        self.theme_combo.pack(side=tk.LEFT)
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)

        # status area: progress bar + label text
        self.spin = ttk.Progressbar(top, mode="indeterminate", length=150)
        self.spin.pack(side=tk.RIGHT, padx=(8,0))
        self.status = ttk.Label(top, text="Ready.")
        self.status.pack(side=tk.RIGHT, padx=(0,10))

        # ----- split window: input panel on left, output/info tabs on right -----
        paned = ttk.Panedwindow(self.root, orient="horizontal")
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        left = ttk.Frame(paned, width=380)
        right = ttk.Frame(paned)
        paned.add(left, weight=0); paned.add(right, weight=1)

        # input area (text box + buttons + browse image)
        self.input_panel = InputPanel(left, self.on_run1, self.on_run2, self.on_clear, self.on_browse)
        self.input_panel.frame.pack(fill=tk.BOTH, expand=True)

        # preview area (shows small version of chosen image)
        self.preview = OutputPreview(left)
        self.preview.frame.pack(fill=tk.X, expand=False, pady=(8,0))

        # output area on the right: two tabs (results and model info)
        self.nb = ttk.Notebook(right); self.nb.pack(fill=tk.BOTH, expand=True)
        self.output_panel = OutputPanel(self.nb)
        self.info_panel = InfoPanel(self.nb)
        self.nb.add(self.output_panel.frame, text="Results")
        self.nb.add(self.info_panel.frame, text="Info")

        # ----- menu bar (File + Help) -----
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Result", command=self._save_result)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About",
            command=lambda: messagebox.showinfo("About", "HIT137 A3 — Tkinter + Hugging Face + OpenCV"))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menubar)

        # keep track of selected image state
        self.image_state = ImageState()

        # show model info for sentiment by default
        self._refresh_info("sentiment")

        # allow Ctrl+Enter as shortcut for running text analysis
        self.root.bind("<Control-Return>", lambda _: self.on_run1())

    # ----- event handlers -----

    def _on_task_change(self, _):
        # switch model info panel when user changes task
        key = "sentiment" if self.task_var.get().startswith("Text") else "image"
        self._refresh_info(key)

    def _on_theme_change(self, _):
        # update theme when user picks another one
        self.theme.set_theme(self.theme_var.get())

    # run a task in background thread and send result to queue
    def run_async(self, func, on_done):
        if self._busy:
            self._set_status("Busy…")
            return
        self._busy = True
        self.spin.start()
        self._set_status("Running…")

        def worker():
            try:
                res = func()
                self._job_q.put(("ok", res, on_done))
            except Exception as e:
                self._job_q.put(("err", e, None))

        threading.Thread(target=worker, daemon=True).start()

    # check job queue regularly for finished tasks
    def _poll_job_queue(self):
        try:
            while True:
                status, payload, cb = self._job_q.get_nowait()
                if status == "ok":
                    self._last_result = payload
                    if cb: cb(payload)
                    self._set_status("Done.")
                else:
                    messagebox.showerror("Error", str(payload))
                    self._set_status("Error.")
                self.spin.stop()
                self._busy = False
        except queue.Empty:
            pass
        self.root.after(100, self._poll_job_queue)

    def _set_status(self, text: str):
        # update the status text shown on top bar
        self.status.configure(text=text)

    def _refresh_info(self, key: str):
        # update info tab with current model details
        model = self.mm.get(key)
        self.info_panel.model_info.config(state="normal")
        self.info_panel.model_info.delete("1.0", tk.END)
        self.info_panel.model_info.insert("1.0", model.info())
        self.info_panel.model_info.config(state="disabled")

    @error_handler
    def on_browse(self):
        # let user pick an image file
        path = filedialog.askopenfilename(
            filetypes=[('Image files','*.png;*.jpg;*.jpeg;*.bmp;*.gif')])
        if not path: return
        from .utils.imaging import load_image
        self.image_state.path = path
        self.image_state.image = load_image(path)
        self.preview.show_image(self.image_state.image)
        self.nb.select(self.output_panel.frame)

    @error_handler
    def on_run1(self):
        # run text sentiment analysis
        if self.input_panel.input_var.get() != "Text":
            raise ValueError("Input Type is not Text. Choose Text to run sentiment.")
        txt = self.input_panel.text_area.get("1.0", tk.END).strip()
        if not txt:
            raise ValueError("Please enter some text first.")
        self._refresh_info("sentiment")
        # temporary placeholder until model finishes
        self.output_panel.render([{"label":"...", "score":0.0}])
        self.run_async(lambda: self.mm.run("sentiment", txt), self._on_sentiment_done)

    def _on_sentiment_done(self, rows):
        # update output panel once text analysis is ready
        self.output_panel.render(rows)
        self.nb.select(self.output_panel.frame)

    @error_handler
    def on_run2(self):
        # run image classification
        if self.input_panel.input_var.get() != "Image":
            raise ValueError("Input Type is not Image. Choose Image to run classifier.")
        if self.image_state.image is None:
            raise ValueError("Please choose an image first (Browse Image).")
        img = self.image_state.image
        # optional preprocessing using OpenCV
        if getattr(self.input_panel, "use_cv2", None) and self.input_panel.use_cv2.get():
            img = preprocess_image_cv2(img, size=(224, 224), blur=False, edges=False, gray=False)
        self._refresh_info("image")
        self.output_panel.render([{"label":"...", "score":0.0}])
        self.run_async(lambda: self.mm.run("image", img), self._on_image_done)

    def _on_image_done(self, rows):
        # update output once classification results are ready
        self.output_panel.render(rows)
        self.nb.select(self.output_panel.frame)

    def on_clear(self):
        # clear all inputs and outputs, reset state
        self.input_panel.text_area.delete("1.0", tk.END)
        self.output_panel.output_text.delete("1.0", tk.END)
        self.output_panel.table.load([])
        self.preview.label.configure(image="", text="(no image)")
        self._last_result = None
        self._set_status("Cleared.")

    def _save_result(self):
        # save last model output to JSON file
        if not self._last_result:
            messagebox.showinfo("Save Result", "Nothing to save yet. Run a model first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json"),("All files","*.*")],
            initialfile="result.json")
        if not path: return
        import json, pathlib
        pathlib.Path(path).write_text(json.dumps(self._last_result, indent=2), encoding="utf-8")
        self._set_status("Saved.")
