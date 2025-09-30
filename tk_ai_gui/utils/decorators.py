from __future__ import annotations 
import functools, time, logging
from typing import Callable
import tkinter as tk
from tkinter import messagebox

# Set up logging so that important info is printed to the console
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# This decorator keeps track of when a function is called and what it returns
def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__}")  # show that the function started
        result = func(*args, **kwargs)  # actually run the function
        s = str(result)  # turn the result into text
        # log the function result (trimmed if it's too long)
        logging.info(f"{func.__name__} -> {s[:180] + ('...' if len(s)>180 else '')}")
        return result  # send the result back
    return wrapper

# This decorator measures how long a function takes to run
def time_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # mark the starting time
        try:
            return func(*args, **kwargs)  # run the function normally
        finally:
            dt = (time.perf_counter() - start) * 1000  # calculate time in ms
            logging.info(f"{func.__name__} took {dt:.1f} ms")  # log how long it took
    return wrapper

# This decorator handles errors so the program doesn’t crash unexpectedly
def error_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # try running the function
        except Exception as e:  # if something goes wrong
            # If the object passed in has a text box, show the error there
            for a in args:
                if hasattr(a, "output_text") and isinstance(getattr(a, "output_text"), tk.Text):
                    a.output_text.delete("1.0", tk.END)
                    a.output_text.insert(tk.END, f"Error: {e}")
                    return
            # Otherwise, pop up a message box with the error
            messagebox.showerror("Error", str(e))
    return wrapper
