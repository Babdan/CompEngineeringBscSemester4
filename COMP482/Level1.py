import tkinter as tk
from tkinter import filedialog
import os
from collections import defaultdict

# Dorantes-Nikolaev, Bogdan Itsam
# 3/08/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 1

def compress():
    filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filename:
        return

    with open(filename, 'r') as f:
        data = f.read()

    # Construct the LZW dictionary
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}

    w = ""
    result = []
    for c in data:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    if w:
        result.append(dictionary[w])

    # Save the compressed file
    output_filename = os.path.splitext(filename)[0] + "_LZWcomp" + os.path.splitext(filename)[1]
    with open(output_filename, 'w') as f:
        for code in result:
            f.write(f"{code}\n")

    # Calculate code length and compression ratio
    code_length = len(result)
    compression_ratio = len(data) / code_length

    # Show popup with code length and compression ratio
    tk.messagebox.showinfo("Compression Results",
                           f"Code length: {code_length}\nCompression ratio: {compression_ratio:.2f}")


def decompress():
    filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filename:
        return

    with open(filename, 'r') as f:
        compressed_data = [int(line.strip()) for line in f.readlines()]

    # Restore the LZW dictionary
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}

    result = []
    w = chr(compressed_data.pop(0))
    result.append(w)
    for k in compressed_data:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError(f'Bad compressed k: {k}')
        result.append(entry)

        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        w = entry

    # Save the restored text
    output_filename = os.path.splitext(filename)[0] + "_LZWdecomp" + os.path.splitext(filename)[1]
    with open(output_filename, 'w') as f:
        f.write(''.join(result))

    # Compare original and restored text
    original_filename = os.path.splitext(filename)[0][:-8] + os.path.splitext(filename)[1]
    with open(original_filename, 'r') as f:
        original_data = f.read()

    if original_data == ''.join(result):
        tk.messagebox.showinfo("Decompression Results", "Original and restored text are identical.")
    else:
        tk.messagebox.showerror("Decompression Results", "Original and restored text are different.")


root = tk.Tk()
root.title("LZW Text Compression (Level 1)")
root.geometry("365x70")
compress_button = tk.Button(root, text="Compress", command=compress)
compress_button.pack()
decompress_button = tk.Button(root, text="Decompress", command=decompress)
decompress_button.pack()
root.mainloop()
