import numpy as np
from PIL import Image

def read_and_prepare_image(image_path, size=None):
    with Image.open(image_path) as img:
        img_gray = img.convert('L')
        if size:
            img_gray = img_gray.resize(size)
        return np.array(img_gray, dtype=np.int64)

def matrix_mod_inv(matrix, modulus):
    det = int(np.round(np.linalg.det(matrix)))
    det_inv = pow(det, -1, modulus)
    adjugate = det_inv * np.round(det * np.linalg.inv(matrix)).astype(int)
    return np.mod(adjugate, modulus)


def hill_cipher_image(image_array, key, mode='encrypt'):
    key_matrix = prepare_key(key)
    block_size = key_matrix.shape[0]
    h, w = image_array.shape
    
    if mode == 'decrypt':
        key_matrix = matrix_mod_inv(key_matrix, 256)
    
    result = np.zeros_like(image_array, dtype=np.int64)
    
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = image_array[i:i+block_size, j:j+block_size]
            if block.shape[0] < block_size or block.shape[1] < block_size:
                padded_block = np.pad(block, ((0, block_size - block.shape[0]), (0, block_size - block.shape[1])), mode='constant')
            else:
                padded_block = block
            
            encoded_block = np.dot(key_matrix, padded_block) % 256
            result[i:i+block_size, j:j+block_size] = encoded_block[:block.shape[0], :block.shape[1]]
    
    return result.astype(np.uint8)

def prepare_key(key_image):
    h, w = key_image.shape
    size = min(h, w)
    key_matrix = key_image[:size, :size]
    return key_matrix

def save_image(image_array, path):
    Image.fromarray(image_array).save(path)
# Example usage
plaintext_path = "nature.jpg"
key_path = "keyimage.jpg"

plaintext_array = read_and_prepare_image(plaintext_path)
key_array = read_and_prepare_image(key_path)

encrypted_array = hill_cipher_image(plaintext_array, key_array, mode='encrypt')
decrypted_array = hill_cipher_image(encrypted_array, key_array, mode='decrypt')

save_image(encrypted_array, 'hill_encrypted_image.png')
save_image(decrypted_array, 'hill_decrypted_image.png')