from __future__ import annotations
import tkinter as tk
from .app import MainWindow

# this function is the starting point of the program
def main():
    # make the main Tkinter window (the base of our GUI)
    root = tk.Tk()

    # create our MainWindow class and connect it with the root window
    MainWindow(root)

    # keep the program running until the user closes the window
    root.mainloop()

# this makes sure the main() runs only when we run this file directly
if __name__ == "__main__":
    main()
