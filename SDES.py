import hashlib
import numpy as np
from PIL import Image


def permute(bits, perm):
    return [bits[i] for i in perm]


def left_shift(bits, shifts):
    return bits[shifts:] + bits[:shifts]


def s_box_lookup(s_box, row, col):
    return s_box[row][col]


def xor(bits1, bits2):
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]


def to_bits(string):
    return [int(bit) for char in string for bit in f"{ord(char):08b}"]


def from_bits(bits):
    return "".join(
        chr(int("".join(map(str, bits[i : i + 8])), 2)) for i in range(0, len(bits), 8)
    )


# Permutation and S-Box Tables
IP = [1, 5, 2, 0, 3, 7, 4, 6]
IP1 = [3, 0, 2, 4, 6, 1, 7, 5]
EP = [3, 0, 1, 2, 1, 2, 3, 0]

S0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
S1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]

P4 = [1, 3, 2, 0]


def f_function(right, key):
    expanded_right = permute(right, EP)
    xor_result = xor(expanded_right, key)

    left_sbox = xor_result[:4]
    right_sbox = xor_result[4:]

    row_s0 = (left_sbox[0] << 1) | left_sbox[3]
    col_s0 = (left_sbox[1] << 1) | left_sbox[2]
    s0_result = s_box_lookup(S0, row_s0, col_s0)

    row_s1 = (right_sbox[0] << 1) | right_sbox[3]
    col_s1 = (right_sbox[1] << 1) | right_sbox[2]
    s1_result = s_box_lookup(S1, row_s1, col_s1)

    sbox_output = [
        (s0_result >> 1) & 1,
        s0_result & 1,
        (s1_result >> 1) & 1,
        s1_result & 1,
    ]
    permuted_output = permute(sbox_output, P4)

    return permuted_output


def encrypt_block(block, k1, k2):
    block = [int(b) for b in block]
    block = permute(block, IP)

    left, right = block[:4], block[4:]

    f_result = f_function(right, k1)
    left = xor(left, f_result)

    left, right = right, left

    f_result = f_function(right, k2)
    left = xor(left, f_result)

    combined = left + right
    ciphertext = permute(combined, IP1)

    return "".join(map(str, ciphertext))


def sdes_key_generation(key_10bit):
    P10 = [2, 4, 1, 6, 3, 9, 0, 8, 7, 5]
    P8 = [5, 2, 6, 3, 7, 4, 9, 8]

    permuted_key = permute([int(b) for b in key_10bit], P10)
    left_half, right_half = permuted_key[:5], permuted_key[5:]

    left_half = left_shift(left_half, 1)
    right_half = left_shift(right_half, 1)
    key1 = permute(left_half + right_half, P8)

    left_half = left_shift(left_half, 2)
    right_half = left_shift(right_half, 2)
    key2 = permute(left_half + right_half, P8)

    return key1, key2


def encrypt_text(text, key_10bit):
    key1, key2 = sdes_key_generation(key_10bit)

    blocks = [text[i : i + 8] for i in range(0, len(text), 8)]
    encrypted_blocks = [encrypt_block(block, key1, key2) for block in blocks]

    return from_bits([int(b) for block in encrypted_blocks for b in block])


def decrypt_block(block, k1, k2):
    # Convert block to list of bits
    block = [int(b) for b in block]
    # Apply Initial Permutation (IP)
    block = permute(block, IP)

    # Split into left and right halves
    left, right = block[:4], block[4:]

    # Apply Feistel function with key k2
    f_result = f_function(right, k2)
    left = xor(left, f_result)

    # Swap left and right
    left, right = right, left

    # Apply Feistel function with key k1
    f_result = f_function(right, k1)
    left = xor(left, f_result)

    # Combine halves
    combined = left + right
    # Apply Inverse Permutation (IP1)
    plaintext_bits = permute(combined, IP1)

    return "".join(map(str, plaintext_bits))


def decrypt_text(encrypted_text, key_10bit):
    key1, key2 = sdes_key_generation(key_10bit)

    # Ensure encrypted text is in bits
    encrypted_bits = to_bits(encrypted_text)

    # Split into 8-bit blocks
    blocks = [encrypted_bits[i : i + 8] for i in range(0, len(encrypted_bits), 8)]
    decrypted_blocks = [decrypt_block(block, key1, key2) for block in blocks]

    return from_bits([int(b) for block in decrypted_blocks for b in block])


def image_to_text(image_path):
    # Open the image and convert to grayscale
    image = Image.open(image_path).convert("L")  # 'L' mode converts to grayscale

    # Convert image to numpy array
    image_array = np.array(image)

    # Flatten the array into a 1D array of pixel values
    flattened_array = image_array.flatten()

    # Convert the array into a text string
    text = "".join(chr(pixel) for pixel in flattened_array)

    return text, image_array.shape


def text_to_image(text, shape, output_path):
    # Convert text back to pixel values
    pixel_values = [ord(char) for char in text]
    
    # Ensure the pixel values match the shape of the original image
    if len(pixel_values) != np.prod(shape):
        raise ValueError("Text length does not match the size of the original image.")
    
    # Reshape the pixel values to the original shape
    image_array = np.array(pixel_values).reshape(shape)
    
    # Create an image from the pixel values
    image = Image.fromarray(image_array.astype(np.uint8))
    
    # Save or show the image
    image.save(output_path)
    print(f"Image saved to {output_path}")

# Example usage
key_10bit = "1010000010"  # Example 10-bit key
# text = hashlib.sha256(input("Enter Input: ").encode()).hexdigest()

img = image_to_text("nature.jpg")


binary_text = to_bits(img[0])
encrypted_text = encrypt_text(binary_text, key_10bit)
text_to_image(encrypted_text,img[1],"SDES_encrypted.jpg")

decrypted_text = decrypt_text(encrypted_text, key_10bit)
text_to_image(decrypted_text,img[1],"SDES_decrypted.jpg")
