import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import numpy as np
import os

# Dorantes-Nikolaev, Bogdan Itsam
# 3/19/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 4

def compress():
    # Open file dialog to select image file
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    # Open image using PIL and convert to RGB format if necessary
    img = Image.open(file_path).convert("RGB")
    width, height = img.size

    # Split image into RGB components
    r, g, b = img.split()

    # Convert RGB components into numpy arrays
    r_arr = np.array(r).ravel()
    g_arr = np.array(g).ravel()
    b_arr = np.array(b).ravel()

    # Initialize LZW dictionaries for each component
    r_dict = {chr(i): i for i in range(256)}
    g_dict = {chr(i): i for i in range(256)}
    b_dict = {chr(i): i for i in range(256)}

    # Compress each component using LZW algorithm
    r_comp_data = lzw_compress(r_arr, r_dict)
    g_comp_data = lzw_compress(g_arr, g_dict)
    b_comp_data = lzw_compress(b_arr, b_dict)

    # Concatenate compressed data for all components
    comp_data = np.concatenate(([0xFFFF], r_comp_data, [0xFFFF], g_comp_data, [0xFFFF], b_comp_data))

    # Save compressed data to file
    comp_file_path = file_path.rsplit(".", 1)[0] + "_compressed.npz"
    np.savez_compressed(comp_file_path, comp_data=comp_data, r_dict=r_dict, g_dict=g_dict, b_dict=b_dict, width=width, height=height)

    # Calculate and display entropy, average code length,
    # compressed file size and compression ratio
    ent_r = entropy(r_arr)
    ent_g = entropy(g_arr)
    ent_b = entropy(b_arr)
    avg_ent = (ent_r + ent_g + ent_b) / 3

    avg_len_r = avg_code_length(r_comp_data)
    avg_len_g = avg_code_length(g_comp_data)
    avg_len_b = avg_code_length(b_comp_data)
    avg_len = (avg_len_r + avg_len_g + avg_len_b) / 3

    comp_file_size = os.path.getsize(comp_file_path)
    orig_file_size = os.path.getsize(file_path)
    comp_ratio = orig_file_size / comp_file_size

    msg = f"Entropy: {avg_ent:.2f}\nAverage code length: {avg_len:.2f}\nCompressed file size: {comp_file_size} bytes\nCompression ratio: {comp_ratio:.2f}"
    tk.messagebox.showinfo("Compression Results", msg)


def decompress():
    # Open file dialog to select compressed data file
    file_path = filedialog.askopenfilename(filetypes=[("Compressed Data Files", "*.npz")])
    if not file_path:
        return

    # Load compressed data and dictionaries from file
    npzfile = np.load(file_path, allow_pickle=True)
    comp_data = npzfile["comp_data"]
    r_dict = npzfile["r_dict"].item()
    g_dict = npzfile["g_dict"].item()
    b_dict = npzfile["b_dict"].item()
    width = npzfile["width"].item()
    height = npzfile["height"].item()

    # Reverse dictionaries
    r_dict_inv = {v: k for k, v in r_dict.items()}
    g_dict_inv = {v: k for k, v in g_dict.items()}
    b_dict_inv = {v: k for k, v in b_dict.items()}

    # Decompress each RGB component using LZW algorithm
    marker_indices = np.where(comp_data == 0xFFFF)[0]
    r_decomp_data = lzw_decompress(comp_data[marker_indices[0]+1:marker_indices[1]], r_dict_inv)
    g_decomp_data = lzw_decompress(comp_data[marker_indices[1]+1:marker_indices[2]], g_dict_inv)
    b_decomp_data = lzw_decompress(comp_data[marker_indices[2]+1:], b_dict_inv)

    # Reshape decompressed data into 2D arrays
    r_arr = np.reshape(r_decomp_data, (height, width))
    g_arr = np.reshape(g_decomp_data, (height, width))
    b_arr = np.reshape(b_decomp_data, (height, width))

    # Merge RGB components into single image using PIL
    r = Image.fromarray(r_arr)
    g = Image.fromarray(g_arr)
    b = Image.fromarray(b_arr)
    img = Image.merge("RGB", (r, g, b))

    # Save restored image to file
    img_file_path = file_path.rsplit(".", 1)[0] + "_recovered.png"
    img.save(img_file_path)

    # Find the original image path
    orig_img_base_path = file_path.rsplit("_compressed", 1)[0]
    orig_img_ext = None
    for ext in [".png", ".jpg", ".jpeg"]:
        if os.path.exists(orig_img_base_path + ext):
            orig_img_ext = ext
            break

    if orig_img_ext is None:
        orig_img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not orig_img_path:
            return
    else:
        orig_img_path = orig_img_base_path + orig_img_ext

    # Open original and recovered images using PIL
    orig_img = Image.open(orig_img_path)
    recovered_img = Image.open(img_file_path)

    # Create a new window for side-by-side comparison
    compare_window = tk.Toplevel(root)
    compare_window.title("Image Comparison")

    # Convert PIL images to ImageTk PhotoImage objects
    orig_img_tk = ImageTk.PhotoImage(orig_img)
    recovered_img_tk = ImageTk.PhotoImage(recovered_img)

    # Create labels to display images and pack them
    orig_img_label = tk.Label(compare_window, image=orig_img_tk)
    orig_img_label.image = orig_img_tk
    orig_img_label.pack(side=tk.LEFT)

    recovered_img_label = tk.Label(compare_window, image=recovered_img_tk)
    recovered_img_label.image = recovered_img_tk
    recovered_img_label.pack(side=tk.RIGHT)


def lzw_compress(data, dictionary):
    # Initialize variables
    code = 256
    string = ""
    result = []

    # Iterate over data
    for symbol in data:
        # Concatenate string and symbol
        string_plus_symbol = string + chr(symbol)

        # Check if concatenated string is in dictionary
        if string_plus_symbol in dictionary:
            # Update string
            string = string_plus_symbol
        else:
            # Add concatenated string to dictionary and update code
            dictionary[string_plus_symbol] = code
            code += 1

            # Append code for current string to result and update string
            result.append(dictionary[string])
            string = chr(symbol)

    # Append code for final string to result if necessary
    if len(string) > 0:
        result.append(dictionary[string])

    return np.array(result, dtype=np.uint16)


def lzw_decompress(comp_data, dictionary):
    # Initialize variables
    code = 256
    dictionary = {i: chr(i) for i in range(256)}
    result = []

    # Get first code from compressed data and append corresponding string to result
    code = comp_data[0]
    string = dictionary[code]
    result.append(string)

    # Iterate over remaining codes in compressed data
    for code in comp_data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        else:
            entry = string + string[0]

        result.append(entry)

        # Add new entry to dictionary and update code
        if len(dictionary) < 2**16: # Limit the dictionary size to prevent overflow
            dictionary[len(dictionary)] = string + entry[0]

        # Update string
        string = entry

    return np.array([ord(ch) for ch in "".join(result)], dtype=np.uint8)


def entropy(data):
    # Calculate probability for each value in data
    prob = np.bincount(data) / len(data)

    # Calculate and return entropy
    return -np.sum(prob * np.log2(prob + 1e-10))


def avg_code_length(comp_data):
    # Calculate average code length
    return np.mean(np.ceil(np.log2(comp_data + 1)))


if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    root.title("LZW Color Image Compression (Level 4)")
    root.geometry("420x70")

    # Create compress button
    compress_button = tk.Button(root, text="Compress", command=compress)
    compress_button.pack(fill=tk.X)

    # Create decompress button
    decompress_button = tk.Button(root, text="Decompress", command=decompress)
    decompress_button.pack(fill=tk.X)

    # Run main loop
    root.mainloop()
