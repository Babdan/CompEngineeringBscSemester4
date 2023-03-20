import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from collections import defaultdict

# Dorantes-Nikolaev, Bogdan Itsam
# 3/19/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: GUI Menu


# Function to run the LZW compression script in a new thread
def run_lzw_compression():
    if not run_lzw_compression.running:
        selected_file = file_var.get()
        if selected_file:
            script_path = os.path.join("Sourcecode", f"{selected_file}.py")
            run_lzw_compression.running = True
            threading.Thread(target=subprocess.run, args=(["python", script_path],), daemon=True).start()
            run_lzw_compression.running = False

# Create a Tkinter application window
app = tk.Tk()
app.title("LZW Compression Selector")
app.geometry("420x70")

# Create a StringVar to hold the selected file name
file_var = tk.StringVar()

# List of LZW compression scripts without file extensions
lzw_files = [
    "Level1",
    "Level2",
    "Level3",
    "Level4",
    "Level5",
]

# Create a label and add it to the window
label = tk.Label(app, text="Select LZW Compression Algorithm:")
label.pack()

# Create a drop-down menu (Combobox) with the available LZW compression algorithms
file_dropdown = ttk.Combobox(app, textvariable=file_var, values=lzw_files)
file_dropdown.pack()

# Create a button to run the selected LZW compression script
run_button = tk.Button(app, text="Run Algorithm", command=run_lzw_compression)
run_button.pack()

# Add a flag to check if an algorithm is already running
run_lzw_compression.running = False

# Start the Tkinter event loop
app.mainloop()
