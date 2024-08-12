from PIL import Image
import numpy as np
from collections import defaultdict
import string

def load_image(image_path, mode='RGB'):
    image = Image.open(image_path).convert(mode)
    return np.array(image)

def save_image(array, output_path):
    image = Image.fromarray(array)
    image.save(output_path)

def resize_image(image_array, target_shape):
    image = Image.fromarray(image_array)
    resized_image = image.resize((target_shape[1], target_shape[0]))
    return np.array(resized_image)

def flip_chunk(chunk, flip_horizontal):
    return chunk

def convert_to_grayscale(image_array):
    if len(image_array.shape) == 3:  # Convert RGB to grayscale
        return np.dot(image_array[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)
    return image_array

def process_chunks(nature, key, chunk_size):
    height, width = nature.shape
    num_chunks_x = width // chunk_size
    num_chunks_y = height // chunk_size

    encrypted_chunks = np.zeros_like(nature)
    for y in range(num_chunks_y):
        for x in range(num_chunks_x):
            nature_chunk = nature[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size]
            key_chunk = key[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size]
            
            flip_horizontal = (x + y) % 2 == 0
            if flip_horizontal:
                key_chunk = flip_chunk(key_chunk, flip_horizontal)

            encrypted_chunk = np.clip(nature_chunk + key_chunk, 0, 255).astype(np.uint8)
            encrypted_chunks[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size] = encrypted_chunk

    return encrypted_chunks

# Define Playfair cipher functions
def create_playfair_matrix(key):
    key = key.upper().replace('J', 'I')
    matrix = []
    used = set()
    for char in key:
        if char not in used and char in string.ascii_uppercase:
            used.add(char)
            matrix.append(char)
    for char in string.ascii_uppercase:
        if char not in used and char != 'J':
            used.add(char)
            matrix.append(char)
    return np.array(matrix).reshape(5, 5)

def playfair_encrypt(plain_text, matrix):
    def digraphs(text):
        text = text.upper().replace('J', 'I')
        digraphs = []
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i] != text[i + 1]:
                digraphs.append(text[i] + text[i + 1])
                i += 2
            else:
                digraphs.append(text[i] + 'X')
                i += 1
        return digraphs

    def find_position(char):
        row, col = np.where(matrix == char)
        return int(row[0]), int(col[0])

    encrypted_text = []
    for digraph in digraphs(plain_text):
        row1, col1 = find_position(digraph[0])
        row2, col2 = find_position(digraph[1])
        if row1 == row2:
            encrypted_text.append(matrix[row1, (col1 + 1) % 5])
            encrypted_text.append(matrix[row2, (col2 + 1) % 5])
        elif col1 == col2:
            encrypted_text.append(matrix[(row1 + 1) % 5, col1])
            encrypted_text.append(matrix[(row2 + 1) % 5, col2])
        else:
            encrypted_text.append(matrix[row1, col2])
            encrypted_text.append(matrix[row2, col1])
    return ''.join(encrypted_text)

def playfair_decrypt(encrypted_text, matrix):
    def digraphs(text):
        text = text.upper()
        return [text[i:i+2] for i in range(0, len(text), 2)]

    def find_position(char):
        row, col = np.where(matrix == char)
        return int(row[0]), int(col[0])

    decrypted_text = []
    for digraph in digraphs(encrypted_text):
        row1, col1 = find_position(digraph[0])
        row2, col2 = find_position(digraph[1])
        if row1 == row2:
            decrypted_text.append(matrix[row1, (col1 - 1) % 5])
            decrypted_text.append(matrix[row2, (col2 - 1) % 5])
        elif col1 == col2:
            decrypted_text.append(matrix[(row1 - 1) % 5, col1])
            decrypted_text.append(matrix[(row2 - 1) % 5, col2])
        else:
            decrypted_text.append(matrix[row1, col2])
            decrypted_text.append(matrix[row2, col1])
    return ''.join(decrypted_text).replace('X', '')

def encrypt_image(nature_path, key_path, encrypted_path, chunk_size):
    nature = load_image(nature_path, 'RGB')
    key = load_image(key_path, 'RGB')
    
    nature_gray = convert_to_grayscale(nature)
    key_gray = convert_to_grayscale(key)
    
    if nature_gray.shape != key_gray.shape:
        key_gray = resize_image(key_gray, nature_gray.shape)
    
    encrypted = process_chunks(nature_gray, key_gray, chunk_size)
    save_image(encrypted, encrypted_path)

def decrypt_image(encrypted_path, key_path, decrypted_path, chunk_size):
    encrypted = load_image(encrypted_path, 'RGB')
    key = load_image(key_path, 'RGB')
    
    encrypted_gray = convert_to_grayscale(encrypted)
    key_gray = convert_to_grayscale(key)
    
    if encrypted_gray.shape != key_gray.shape:
        key_gray = resize_image(key_gray, encrypted_gray.shape)
    
    height, width = encrypted_gray.shape
    num_chunks_x = width // chunk_size
    num_chunks_y = height // chunk_size
    
    decrypted_chunks = np.zeros_like(encrypted_gray)
    for y in range(num_chunks_y):
        for x in range(num_chunks_x):
            encrypted_chunk = encrypted_gray[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size]
            key_chunk = key_gray[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size]
            
            flip_horizontal = (x + y) % 2 == 0
            if flip_horizontal:
                key_chunk = flip_chunk(key_chunk, flip_horizontal)

            decrypted_chunk = np.clip(encrypted_chunk - key_chunk, 0, 255).astype(np.uint8)
            decrypted_chunks[y*chunk_size:(y+1)*chunk_size, x*chunk_size:(x+1)*chunk_size] = decrypted_chunk

    save_image(decrypted_chunks, decrypted_path)

# Example usage
nature_image_path = 'nature.jpg'
key_image_path = 'key.jfif'
encrypted_image_path = 'encrypted.jpg'
decrypted_image_path = 'decrypted.jpg'
chunk_size = 256  # Define the size of the chunks (e.g., 256x256 pixels)

encrypt_image(nature_image_path, key_image_path, encrypted_image_path, chunk_size)
decrypt_image(encrypted_image_path, key_image_path, decrypted_image_path, chunk_size)
