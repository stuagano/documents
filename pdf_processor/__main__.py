#!/usr/bin/env python3
from pdf_processor.ui.simple_ui import SimpleUI  # Import SimpleUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = SimpleUI(root)  # Instantiate SimpleUI
    root.mainloop()

if __name__ == '__main__':
    main()