#!/usr/bin/env python3
from pdf_processor.GUI.simple_ui import PDFProcessorGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = PDFProcessorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()