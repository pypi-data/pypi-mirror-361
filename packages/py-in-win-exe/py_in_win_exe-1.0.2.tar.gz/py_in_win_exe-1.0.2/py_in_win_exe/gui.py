import tkinter as tk
from tkinter import filedialog
from .compiler import compile_script

def run_gui():
    def select_file():
        file = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        entry_script.delete(0, tk.END)
        entry_script.insert(0, file)

    root = tk.Tk()
    root.title("Py-in-Win-EXE")
    
    tk.Label(root, text="Script:").grid(row=0, column=0)
    entry_script = tk.Entry(root, width=40)
    entry_script.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2)

    tk.Label(root, text="Output name:").grid(row=1, column=0)
    entry_output = tk.Entry(root, width=40)
    entry_output.grid(row=1, column=1)

    tk.Button(root, text="Compile", command=lambda: compile_script(
        entry_script.get(),
        entry_output.get() or "output"
    )).grid(row=2, column=1)

    root.mainloop()