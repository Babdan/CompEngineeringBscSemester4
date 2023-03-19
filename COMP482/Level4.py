import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import math

# Dorantes-Nikolaev, Bogdan Itsam
# 3/08/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 4


def compress():
    # Select image file
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not filepath:
        return

    # Open image and decompose into RGB components
    im = Image.open(filepath)
    im = im.convert('RGB')  # Convert to RGB if image is RGBA
    r, g, b = im.split()

    # Convert RGB components to numpy arrays
    r = np.array(r)
    g = np.array(g)
    b = np.array(b)

    # Initialize LZW dictionary for each component
    dict_r = {str(i): str(i) for i in range(256)}
    dict_g = {str(i): str(i) for i in range(256)}
    dict_b = {str(i): str(i) for i in range(256)}

    # Compress each component using LZW algorithm
    compressed_r = lzw_compress(r.flatten(), dict_r)
    compressed_g = lzw_compress(g.flatten(), dict_g)
    compressed_b = lzw_compress(b.flatten(), dict_b)

    # Convert the dictionaries' keys to integers
    dict_r = {int(k): v for k, v in dict_r.items()}
    dict_g = {int(k): v for k, v in dict_g.items()}
    dict_b = {int(k): v for k, v in dict_b.items()}

    print("compressed_r:", compressed_r)  # Debugging
    print("compressed_g:", compressed_g)  # Debugging
    print("compressed_b:", compressed_b)  # Debugging
    print("dict_r:", dict_r)  # Debugging
    print("dict_g:", dict_g)  # Debugging
    print("dict_b:", dict_b)  # Debugging

    # Concatenate compressed data for all components
    compressed_data = np.concatenate((compressed_r, compressed_g, compressed_b))

    # Convert compressed_data to integers
    compressed_data = compressed_data.astype(int)

    # Calculate entropy and average code length
    p = np.bincount(compressed_data) / len(compressed_data)
    p = p[p > 0]
    H = -np.sum(p * np.log2(p))
    L = len(compressed_data) * H / 8

    # Save compressed data to file
    filedir, filename = os.path.split(filepath)
    filename = os.path.splitext(filename)[0]
    compressed_filename = os.path.join(filedir, filename + "_compressed.npz")
    print(f"Saving compressed data to {compressed_filename}")  # For debugging
    np.savez_compressed(compressed_filename,
                        compressed_r=compressed_r,
                        compressed_g=compressed_g,
                        compressed_b=compressed_b,
                        dict_r=dict_r,
                        dict_g=dict_g,
                        dict_b=dict_b)
    print("Compressed data saved successfully")  # For debugging

    # Calculate compression ratio
    original_size = os.path.getsize(filepath)
    compressed_size = os.path.getsize(compressed_filename)
    compression_ratio = original_size / compressed_size

    # Display compression results in popup window
    tk.messagebox.showinfo("Compression Results",
                           f"Entropy: {H:.2f}\nAverage Code Length: {L:.2f}\nCompressed File Size: {compressed_size} bytes\nCompression Ratio: {compression_ratio:.2f}")


def decompress():
    # Select compressed data file
    filepath = filedialog.askopenfilename(filetypes=[("NPZ Files", "*.npz")])
    if not filepath:
        return

    # Load compressed data and dictionaries from file
    with np.load(filepath, allow_pickle=True) as compressed_data_file:
        compressed_r = compressed_data_file['compressed_r']
        compressed_g = compressed_data_file['compressed_g']
        compressed_b = compressed_data_file['compressed_b']
        dict_r = compressed_data_file['dict_r'].item()
        dict_g = compressed_data_file['dict_g'].item()
        dict_b = compressed_data_file['dict_b'].item()

    print("compressed_r:", compressed_r)  # Debugging
    print("compressed_g:", compressed_g)  # Debugging
    print("compressed_b:", compressed_b)  # Debugging

    # Convert the dictionaries' keys to integers
    dict_r = {int(k): v for k, v in dict_r.items()}
    dict_g = {int(k): v for k, v in dict_g.items()}
    dict_b = {int(k): v for k, v in dict_b.items()}

    print("dict_r:", dict_r)  # Debugging
    print("dict_g:", dict_g)  # Debugging
    print("dict_b:", dict_b)  # Debugging

    # Decompress each component using LZW algorithm
    decompressed_r = lzw_decompress(compressed_r, dict_r)
    decompressed_g = lzw_decompress(compressed_g, dict_g)
    decompressed_b = lzw_decompress(compressed_b, dict_b)

    # Reshape decompressed data into 2D arrays
    size = int(math.sqrt(len(decompressed_r)))
    r = np.reshape(decompressed_r, (size, size))
    g = np.reshape(decompressed_g, (size, size))
    b = np.reshape(decompressed_b, (size, size))

    # Merge RGB components into single image
    im = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))

    # Save restored image to file
    filename = filepath.split("/")[-1].split(".")[0]
    im.save(filename + "_recovered.png")


def lzw_compress(data, dict):
    max_dict_size = 4096
    w = str(data[0])
    result = []
    dict_size = len(dict)

    for c in data[1:]:
        wc = f"{w}_{c}"
        if wc in dict:
            w = wc
        else:
            result.append(dict[w])
            if dict_size < max_dict_size:
                dict[wc] = dict_size, c
                dict_size += 1
            else:
                dict = {str(i): (i,) for i in range(256)}
                dict_size = len(dict)
            w = str(c)

    result.append(dict[w])

    return np.array(result)


def lzw_decompress(compressed_data, dict):
    max_dict_size = 4096
    result = []
    dict_size = len(dict)

    try:
        w = dict[compressed_data[0]]
    except KeyError:
        raise ValueError("Invalid compressed data")

    result.extend(w)

    for k in compressed_data[1:]:
        try:
            entry = dict[k]
        except KeyError:
            if k == dict_size:
                entry = w + (w[0],)
            else:
                raise ValueError("Invalid compressed data")

        result.extend(entry)

        if dict_size < max_dict_size:
            dict[dict_size] = f"{w}_{entry[0]}"
            dict_size += 1
        else:
            dict = {i: (i,) for i in range(256)}
            dict_size = len(dict)

        w = entry

    return np.array(result, dtype=int)


# Create GUI with Compress and Decompress buttons
root = tk.Tk()
root.title("LZW Color Image Compression (Level 4)")
root.geometry("420x70")
compress_button = tk.Button(root, text="Compress", command=compress)
compress_button.pack(fill=tk.X)
decompress_button = tk.Button(root, text="Decompress", command=decompress)
decompress_button.pack(fill=tk.X)
root.mainloop()
