from __future__ import annotations
import functools, time, logging
from typing import Callable
import tkinter as tk
from tkinter import messagebox

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        s = str(result)
        logging.info(f"{func.__name__} -> {s[:180] + ('...' if len(s)>180 else '')}")
        return result
    return wrapper

def time_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            dt = (time.perf_counter() - start) * 1000
            logging.info(f"{func.__name__} took {dt:.1f} ms")
    return wrapper

def error_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for a in args:
                if hasattr(a, "output_text") and isinstance(getattr(a, "output_text"), tk.Text):
                    a.output_text.delete("1.0", tk.END)
                    a.output_text.insert(tk.END, f"Error: {e}")
                    return
            messagebox.showerror("Error", str(e))
    return wrapper
