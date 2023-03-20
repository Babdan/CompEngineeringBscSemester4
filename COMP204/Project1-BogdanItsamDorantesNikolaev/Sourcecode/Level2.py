import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
import os
import math


# Dorantes-Nikolaev, Bogdan Itsam
# 3/08/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 2

def compress():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if not file_path:
        return
    img = Image.open(file_path)
    img = img.convert('L')
    width, height = img.size
    pixels = list(img.getdata())
    dictionary_size = 256
    dictionary = {chr(i): i for i in range(dictionary_size)}
    string = ""
    compressed_data = []
    for pixel in pixels:
        symbol = chr(pixel)
        if string + symbol in dictionary:
            string = string + symbol
        else:
            compressed_data.append(dictionary[string])
            dictionary[string + symbol] = dictionary_size
            dictionary_size += 1
            string = symbol

    if string:
        compressed_data.append(dictionary[string])

    # Calculate entropy
    pixel_counts = {}
    for pixel in pixels:
        if pixel in pixel_counts:
            pixel_counts[pixel] += 1
        else:
            pixel_counts[pixel] = 1
    pixel_probabilities = [count / (width * height) for count in pixel_counts.values()]
    entropy = -sum(prob * math.log2(prob) for prob in pixel_probabilities)
    # Calculate average code length
    average_code_length = sum(len(bin(code)[2:]) for code in compressed_data) / len(compressed_data)
    # Save compressed file
    compressed_file_path = os.path.splitext(file_path)[0] + "_LZWcomp" + ".txt"
    with open(compressed_file_path, "w") as f:
        f.write(f"{width} {height}\n")
        f.write("\n".join(map(str, compressed_data)))

    # Calculate and display results
    original_file_size = os.path.getsize(file_path)
    compressed_file_size = os.path.getsize(compressed_file_path)
    compression_ratio = original_file_size / compressed_file_size
    results = f"Entropy: {entropy:.3f}\nAverage code length: {average_code_length:.3f}\nCompressed file size: {compressed_file_size} bytes\nCompression ratio: {compression_ratio:.3f}"
    messagebox.showinfo("Compression Results", results)


def decompress():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    with open(file_path, "r") as f:
        lines = f.read().split("\n")
        width, height = map(int, lines.pop(0).split())
        compressed_data = list(map(int, lines))

    dictionary_size = 256
    dictionary = {i: chr(i) for i in range(dictionary_size)}
    string = chr(compressed_data.pop(0))
    result = [string]
    for code in compressed_data:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dictionary_size:
            entry = string + string[0]
        else:
            raise ValueError("Invalid compressed data")
        result.append(entry)
        dictionary[dictionary_size] = string + entry[0]
        dictionary_size += 1
        string = entry

    pixels = [ord(char) for string in result for char in list(string)]
    img = Image.new('L', (width, height))
    img.putdata(pixels)
    decompressed_file_path = os.path.splitext(file_path)[0] + "_LZWdecomp" + ".png"
    img.save(decompressed_file_path)

    # Show decompression results
    compression_description = f"Image was compressed using LZW coding with a dictionary size of 256"
    messagebox.showinfo("Decompression Results", f"Decompression was successful.\n\n{compression_description}")


root = tk.Tk()
root.title("LZW Image Compression (Level 2)")
root.geometry("365x70")
compress_button = tk.Button(root, text="Compress", command=compress)
compress_button.pack(fill=tk.X)
decompress_button = tk.Button(root, text="Decompress", command=decompress)
decompress_button.pack(fill=tk.X)
root.mainloop()
