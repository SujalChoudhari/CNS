from PIL import Image
from pprint import pprint
import numpy as np
from typing import List

def generate_matrix_from_image(key_image_path: str) -> List[List[int]]:
    key_img = Image.open(key_image_path).convert('L')  # Convert to grayscale
    pixels = list(key_img.getdata())
    unique_pixels = []
    seen = set()
    for pixel in pixels:
        if pixel not in seen and len(unique_pixels) < 256:
            seen.add(pixel)
            unique_pixels.append(pixel)
    
    if len(unique_pixels) < 256:
        remaining = [x for x in range(256) if x not in unique_pixels]
        unique_pixels.extend(remaining[:256-len(unique_pixels)])
    
    matrix = [unique_pixels[i*16:(i+1)*16] for i in range(16)]
    return matrix

def encrypt_playfair_image(matrix: List[List[int]], image_path: str) -> Image.Image:
    lookup = {val: (i, j) for i, row in enumerate(matrix) for j, val in enumerate(row)}
    
    img = Image.open(image_path).convert('L') 
    width, height = img.size
    pixels = list(img.getdata())
    
    encrypted_pixels = []
    for i in range(0, len(pixels), 2):
        pixel1 = pixels[i]
        pixel2 = pixels[i+1] if i+1 < len(pixels) else 0
        
        row1, col1 = lookup[pixel1]
        row2, col2 = lookup[pixel2]
        
        if row1 == row2:
            encrypted_pixels.extend([matrix[row1][(col1 + 1) % 16], matrix[row2][(col2 + 1) % 16]])
        elif col1 == col2:
            encrypted_pixels.extend([matrix[(row1 + 1) % 16][col1], matrix[(row2 + 1) % 16][col2]])
        else:
            encrypted_pixels.extend([matrix[row1][col2], matrix[row2][col1]])
    
    encrypted_image = Image.new('L', (width, height))
    encrypted_image.putdata(encrypted_pixels)
    return encrypted_image

def decrypt_playfair_image(matrix: List[List[int]], encrypted_image: Image.Image) -> Image.Image:
    lookup = {val: (i, j) for i, row in enumerate(matrix) for j, val in enumerate(row)}
    
    width, height = encrypted_image.size
    pixels = list(encrypted_image.getdata())
    
    decrypted_pixels = []
    for i in range(0, len(pixels), 2):
        pixel1 = pixels[i]
        pixel2 = pixels[i+1] if i+1 < len(pixels) else 0
        
        row1, col1 = lookup[pixel1]
        row2, col2 = lookup[pixel2]
        
        if row1 == row2:
            decrypted_pixels.extend([matrix[row1][(col1 - 1) % 16], matrix[row2][(col2 - 1) % 16]])
        elif col1 == col2:
            decrypted_pixels.extend([matrix[(row1 - 1) % 16][col1], matrix[(row2 - 1) % 16][col2]])
        else:
            decrypted_pixels.extend([matrix[row1][col2], matrix[row2][col1]])
    
    decrypted_image = Image.new('L', (width, height))
    decrypted_image.putdata(decrypted_pixels)
    return decrypted_image

if __name__ == "__main__":
    key_image_path = "keyimage.jpg"
    input_image_path = "nature.jpg"
    encrypted_image_path = "encrypted_image.png"
    decrypted_image_path = "decrypted_image.png"

    matrix = generate_matrix_from_image(key_image_path)
    pprint(matrix)
    encrypted_image = encrypt_playfair_image(matrix, input_image_path)
    encrypted_image.save(encrypted_image_path)
    
    decrypted_image = decrypt_playfair_image(matrix, encrypted_image)
    decrypted_image.save(decrypted_image_path)

    print("Encryption and decryption completed. Check the output images.")