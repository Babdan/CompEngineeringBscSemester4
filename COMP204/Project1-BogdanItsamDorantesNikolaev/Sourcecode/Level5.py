import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
from collections import defaultdict

# Dorantes-Nikolaev, Bogdan Itsam
# 3/19/2021, COMP 482 Programming Studio, Project 1: Image Compression using LZW coding: Level 5


def compress():
    original_img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])

    if not original_img_path:
        return

    original_img_dir, original_img_name = os.path.split(original_img_path)
    compressed_filename = os.path.splitext(original_img_name)[0] + "_compressed.npz"

    # Save the compressed file in the same directory as the original image
    compressed_path = os.path.join(original_img_dir, compressed_filename)

    original_img = Image.open(original_img_path)
    img = np.array(original_img)

    # Splitting color channels
    r, g, b = img[..., 0], img[..., 1], img[..., 2]

    # Getting the difference images
    diff_r = np.diff(r, axis=1)
    diff_g = np.diff(g, axis=1)
    diff_b = np.diff(b, axis=1)

    # LZW compression
    def lzw_compress(data):
        dictionary = {chr(i): i for i in range(256)}
        word = chr(data[0])
        code = 256
        result = []

        for number in data[1:]:
            char = chr(number)
            if word + char in dictionary:
                word += char
            else:
                result.append(dictionary[word])
                dictionary[word + char] = code
                code += 1
                word = char

        if word:
            result.append(dictionary[word])

        return result, dictionary

    compressed_r, _ = lzw_compress(diff_r.flatten())
    compressed_g, _ = lzw_compress(diff_g.flatten())
    compressed_b, _ = lzw_compress(diff_b.flatten())

    # Saving compressed data along with difference shapes
    np.savez_compressed(compressed_path, r=compressed_r, g=compressed_g, b=compressed_b,
                        r_shape=diff_r.shape, g_shape=diff_g.shape, b_shape=diff_b.shape)

    # Calculate entropy, average code length, the size of the compressed file, and compression ratio
    def entropy(data):
        value_counts = defaultdict(int)
        for number in data:
            value_counts[number] += 1
        probabilities = [count / len(data) for count in value_counts.values()]
        return -sum(p * np.log2(p) for p in probabilities)

    def average_code_length(data):
        return len(data) * 8 / len(np.unique(data))

    compressed_size = os.path.getsize(compressed_path)
    original_size = os.path.getsize(original_img_path)
    compression_ratio = original_size / compressed_size
    entropies = [entropy(channel) for channel in [diff_r.flatten(), diff_g.flatten(), diff_b.flatten()]]
    avg_code_lengths = [average_code_length(channel) for channel in
                        [diff_r.flatten(), diff_g.flatten(), diff_b.flatten()]]

    messagebox.showinfo("Compression Results",
                        f"Entropy: {entropies}\nAverage code length: {avg_code_lengths}\n"
                        f"Compressed size: {compressed_size} bytes\n"
                        f"Compression ratio: {compression_ratio}")


def display_images(original_path, restored_path):
    compare_window = tk.Toplevel(root)
    compare_window.title("Original Image vs Restored Image")

    original_img = Image.open(original_path)
    original_photo = ImageTk.PhotoImage(original_img)
    original_label = tk.Label(compare_window, image=original_photo)
    original_label.image = original_photo
    original_label.grid(row=0, column=0)

    restored_img = Image.open(restored_path)
    restored_photo = ImageTk.PhotoImage(restored_img)
    restored_label = tk.Label(compare_window, image=restored_photo)
    restored_label.image = restored_photo
    restored_label.grid(row=0, column=1)


def find_original_image(compressed_dir, original_img_name):
    extensions = [".png", ".jpg", ".jpeg", ".bmp"]
    for ext in extensions:
        original_img_path = os.path.join(compressed_dir, original_img_name + ext)
        if os.path.exists(original_img_path):
            return original_img_path
    return None


def decompress():
    filetypes = [("Compressed files", "*.npz")]
    compressed_path = filedialog.askopenfilename(title="Select compressed image", filetypes=filetypes)

    if not compressed_path:
        return

    # Try to find the original image based on the compressed file's name
    compressed_dir, compressed_name = os.path.split(compressed_path)
    original_img_name = compressed_name.replace("_compressed.npz", "")
    original_img_path = find_original_image(compressed_dir, original_img_name)

    print(f"Trying to find original image: {original_img_path}")  # Debug print

    # If the original image is not found, ask the user to find it manually
    if not original_img_path:
        print(f"Original image not found, asking user to select it manually.")  # Debug print
        original_img_path = filedialog.askopenfilename(title="Select original image",
                                                        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])

        if not original_img_path:
            return

    img = np.array(Image.open(original_img_path))

    # Load compressed data and difference shapes
    compressed_data = np.load(compressed_path)
    compressed_r = compressed_data['r']
    compressed_g = compressed_data['g']
    compressed_b = compressed_data['b']
    diff_r_shape = compressed_data['r_shape']
    diff_g_shape = compressed_data['g_shape']
    diff_b_shape = compressed_data['b_shape']

    # LZW decompression
    def lzw_decompress(compressed_data, dictionary):
        inverse_dictionary = {v: k for k, v in dictionary.items()}
        word = chr(compressed_data[0])
        result = [ord(c) for c in word]
        for code in compressed_data[1:]:
            if code in inverse_dictionary:
                entry = inverse_dictionary[code]
            elif code == len(inverse_dictionary):
                entry = word + word[0]
            else:
                raise ValueError("Invalid compressed data")

            result.extend(ord(c) for c in entry)
            inverse_dictionary[len(inverse_dictionary)] = word + entry[0]
            word = entry

        return np.array(result)

    # Decompress the color channels
    diff_r_restored = lzw_decompress(compressed_r, {chr(i): i for i in range(256)}).reshape(diff_r_shape)
    diff_g_restored = lzw_decompress(compressed_g, {chr(i): i for i in range(256)}).reshape(diff_g_shape)
    diff_b_restored = lzw_decompress(compressed_b, {chr(i): i for i in range(256)}).reshape(diff_b_shape)

    # Restore the original color channels
    r_restored = np.hstack((np.expand_dims(img[..., 0][:, 0], 1), diff_r_restored)).cumsum(axis=1).astype(np.uint8)
    g_restored = np.hstack((np.expand_dims(img[..., 1][:, 0], 1), diff_g_restored)).cumsum(axis=1).astype(np.uint8)
    b_restored = np.hstack((np.expand_dims(img[..., 2][:, 0], 1), diff_b_restored)).cumsum(axis=1).astype(np.uint8)

    # Combine the color channels
    restored_img = np.stack((r_restored, g_restored, b_restored), axis=-1).astype(np.uint8)

    # Save the restored image
    restored_img_dir, compressed_img_name = os.path.split(compressed_path)
    restored_filename = os.path.splitext(compressed_img_name)[0] + "_restored.png"
    restored_path = os.path.join(restored_img_dir, restored_filename)
    Image.fromarray(restored_img).save(restored_path)

    messagebox.showinfo("Decompression Results",
                        f"Restored image saved as '{restored_filename}'")

    display_images(original_img_path, restored_path)


# Creating the application window
root = tk.Tk()
root.title("LZW Difference Color Image Compression (Level 5)")
root.geometry("469x70")

compress_button = tk.Button(root, text="Compress Image", command=compress)
compress_button.pack(fill=tk.X)

decompress_button = tk.Button(root, text="Decompress Image", command=decompress)
decompress_button.pack(fill=tk.X)

root.mainloop()
