import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import math


# Dorantes-Nikolaev, Bogdan Itsam
# 3/08/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 3

def compress():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    im = Image.open(file_path).convert('L')
    width, height = im.size
    pixel_values = list(im.getdata())
    pixel_values = [pixel_values[i * width:(i + 1) * width] for i in range(height)]

    # Calculate differences
    differences = []
    for row in range(height):
        row_diff = []
        for col in range(width):
            if col == 0:
                row_diff.append(pixel_values[row][col])
            else:
                diff = pixel_values[row][col] - pixel_values[row][col - 1]
                if diff < 0:
                    diff += 256
                row_diff.append(diff)
        differences.append(row_diff)

    # LZW Compression
    dictionary_size = 256
    dictionary = {chr(i): i for i in range(dictionary_size)}

    string = ""
    compressed_data = []
    for row in differences:
        for value in row:
            symbol = chr(value)
            if string + symbol in dictionary:
                string = string + symbol
            else:
                compressed_data.append(dictionary[string])
                dictionary[string + symbol] = dictionary_size
                dictionary_size += 1
                string = symbol

    if string != "":
        compressed_data.append(dictionary[string])

    # Save compressed data to file
    filename, _ = os.path.splitext(os.path.basename(file_path))
    compressed_file_path = os.path.join(os.path.dirname(file_path), f"{filename}_compressed.txt")
    with open(compressed_file_path, 'w') as f:
        f.write(f"{width} {height}\n")
        for data in compressed_data:
            f.write(f"{data}\n")

    # Calculate entropy
    pixel_count = width * height
    value_counts = [0] * 256
    for row in pixel_values:
        for value in row:
            value_counts[value] += 1

    entropy = 0
    for count in value_counts:
        if count == 0:
            continue
        probability = count / pixel_count
        entropy -= probability * math.log2(probability)

    # Calculate average code length and compression ratio
    compressed_size = os.stat(compressed_file_path).st_size
    original_size = os.stat(file_path).st_size

    avg_code_length = compressed_size * 8 / pixel_count
    compression_ratio = original_size / compressed_size

    # Show results in popup window
    popup = tk.Toplevel()
    popup.title("Compression Results")
    results = f"Entropy: {entropy:.2f}\nAverage Code Length: {avg_code_length:.2f}\nCompressed File Size: {compressed_size} bytes\nCompression Ratio: {compression_ratio:.2f}"
    tk.Label(popup, text=results).pack()


def decompress():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    # Load original image
    original_filename, _ = os.path.splitext(os.path.basename(file_path))
    original_image_path = os.path.join(os.path.dirname(file_path), original_filename.replace('_compressed', '') + ".png")

    if not os.path.exists(original_image_path):
        original_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

    original_image = Image.open(original_image_path)

    with open(file_path) as f:
        lines = f.readlines()
        width, height = map(int, lines[0].split())
        compressed_data = [int(line.strip()) for line in lines[1:]]

    # LZW Decompression
    dictionary_size = 256
    dictionary = {i: chr(i) for i in range(dictionary_size)}

    string = chr(compressed_data.pop(0))
    result = [ord(string)]

    for code in compressed_data:
        if code not in dictionary:
            entry = string + string[0]
        else:
            entry = dictionary[code]

        result.extend([ord(c) for c in entry])

        dictionary[dictionary_size] = string + entry[0]
        dictionary_size += 1

        string = entry

    # Restore differences
    differences = []
    row_diff = []
    for value in result:
        if len(row_diff) == width:
            differences.append(row_diff)
            row_diff = []

        if value > 255:
            value -= 256
        row_diff.append(value)

    if row_diff:
        differences.append(row_diff)

    # Restore pixel values
    pixel_values = []
    for row in range(height):
        row_values = []
        for col in range(width):
            if col == 0:
                row_values.append(differences[row][col])
            else:
                value = row_values[col - 1] + differences[row][col]
                if value > 255:
                    value -= 256
                row_values.append(value)
        pixel_values.append(row_values)

    # Create image from pixel values
    im = Image.new('L', (width, height))
    pixel_values_flat = [item for sublist in pixel_values for item in sublist]
    im.putdata(pixel_values_flat)

    # Save image to file with the source filename + "_recovered"
    original_filename, _ = os.path.splitext(os.path.basename(file_path))
    recovered_filename = os.path.join(os.path.dirname(file_path), f"{original_filename}_recovered.png")
    im.save(recovered_filename)

    # Show original and decompressed images side by side in a popup window
    popup = tk.Toplevel()
    popup.title("Original and Decompressed Images")

    original_photo = ImageTk.PhotoImage(original_image)
    original_label = tk.Label(popup, image=original_photo)
    original_label.image = original_photo
    original_label.pack(side="left")

    recovered_photo = ImageTk.PhotoImage(im)
    recovered_label = tk.Label(popup, image=recovered_photo)
    recovered_label.image = recovered_photo
    recovered_label.pack(side="right")


# Create GUI
root = tk.Tk()
root.title("LZW Difference Image Compression (Level 3)")
root.geometry("420x70")

tk.Button(root, text="Compress", command=compress).pack(fill=tk.X)
tk.Button(root, text="Decompress", command=decompress).pack(fill=tk.X)
root.mainloop()
