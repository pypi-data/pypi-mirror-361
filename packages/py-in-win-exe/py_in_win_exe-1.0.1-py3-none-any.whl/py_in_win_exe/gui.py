import os
import subprocess
import tkinter as tk
from tkinter import filedialog

def browse_file(entry):
    filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def browse_icon(entry):
    filename = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def compile_exe():
    script = entry_script.get()
    icon = entry_icon.get()
    name = entry_name.get()
    
    if not script:
        tk.messagebox.showerror("Error", "Select Python script!")
        return

    cmd = [
        os.path.join(os.path.dirname(__file__), "Beta.exe"),
        f"--script={script}",
        f"--name={name}",
        f"--icon={icon}" if icon else ""
    ]
    
    try:
        subprocess.run(cmd, check=True)
        tk.messagebox.showinfo("Success", f"EXE created: {name}.exe")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Compilation failed: {str(e)}")

root = tk.Tk()
root.title("Py-in-Win-EXE")

tk.Label(root, text="Python Script:").pack()
entry_script = tk.Entry(root, width=50)
entry_script.pack()
tk.Button(root, text="Browse", command=lambda: browse_file(entry_script)).pack()

tk.Label(root, text="Icon (optional):").pack()
entry_icon = tk.Entry(root, width=50)
entry_icon.pack()
tk.Button(root, text="Browse", command=lambda: browse_icon(entry_icon)).pack()

tk.Label(root, text="EXE Name:").pack()
entry_name = tk.Entry(root, width=50)
entry_name.pack()

tk.Button(root, text="Compile", command=compile_exe).pack()

root.mainloop()