import numpy as np
from PIL import Image

def mod_inverse(a, m):
    """Compute the modular inverse of a under modulo m."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def encrypt_block(block, key_matrix):
    """Encrypt a block of the image using the Hill cipher key matrix."""
    return np.dot(key_matrix, block) % 256

def decrypt_block(block, inv_key_matrix):
    """Decrypt a block of the image using the Hill cipher inverse key matrix."""
    return np.dot(inv_key_matrix, block) % 256

def hill_cipher_image(image_path, key_matrix, mode='encrypt'):
    """Encrypt or decrypt an image using the Hill cipher."""
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    pixels = np.array(img)

    n = key_matrix.shape[0]

    if mode == 'decrypt':
        det = int(np.round(np.linalg.det(key_matrix)))
        det_inv = mod_inverse(det, 256)

        if det_inv is None:
            raise ValueError("Key matrix is not invertible under mod 256")

        adjugate_matrix = np.round(det * np.linalg.inv(key_matrix)).astype(int) % 256
        inv_key_matrix = (det_inv * adjugate_matrix) % 256
    else:
        inv_key_matrix = None

    # Pad the image to make sure dimensions are divisible by n
    padded_height = (pixels.shape[0] + n - 1) // n * n
    padded_width = (pixels.shape[1] + n - 1) // n * n
    padded_pixels = np.pad(pixels, ((0, padded_height - pixels.shape[0]), 
                                    (0, padded_width - pixels.shape[1])), 
                          mode='constant', constant_values=0)

    processed_pixels = np.copy(padded_pixels)

    for i in range(0, padded_pixels.shape[0], n):
        for j in range(0, padded_pixels.shape[1], n):
            block = padded_pixels[i:i+n, j:j+n]

            if mode == 'encrypt':
                processed_block = encrypt_block(block, key_matrix)
            else:
                processed_block = decrypt_block(block, inv_key_matrix)

            # Ensure block is correctly reshaped back into the image
            processed_pixels[i:i+n, j:j+n] = processed_block

    # Crop padding for the final image
    final_pixels = processed_pixels[:pixels.shape[0], :pixels.shape[1]]

    # Save the processed image
    processed_img = Image.fromarray(final_pixels.astype(np.uint8))
    output_path = image_path.split('.')[0] + ('_encrypted' if mode == 'encrypt' else '_decrypted') + '.png'
    processed_img.save(output_path)

    return output_path

# Define key matrix (must be invertible modulo 256)
key_matrix = np.array( [
   [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
   [6, 8, 10, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
   [0, 8, 10, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
   [0, 8, 10, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
   [0, 8, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
   [0, 8, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
   [0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
]
)

# Path to the image file
image_path = 'nature.jpg'

# Encrypt image
encrypted_image_path = hill_cipher_image(image_path, key_matrix, mode='encrypt')
print(f"Encrypted image saved to: {encrypted_image_path}")

# Decrypt image
decrypted_image_path = hill_cipher_image(encrypted_image_path, key_matrix, mode='decrypt')
print(f"Decrypted image saved to: {decrypted_image_path}")