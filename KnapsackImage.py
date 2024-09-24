import numpy as np
import random
from PIL import Image

def to_binary(pixel_values):
    return "".join(format(val, "08b") for val in pixel_values)

def to_decimal(binary_str):
    return [int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8)]

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

class KnapsackCryptosystem:
    def _init_(self, length=8):
        self.private_key = self.generate_private_key(length)
        self.m = sum(self.private_key) + random.randint(10, 20)
        self.n = random.randint(2, self.m - 1)
        while np.gcd(self.n, self.m) != 1:
            self.n = random.randint(2, self.m - 1)
        self.public_key = [(self.n * pk_elem) % self.m for pk_elem in self.private_key]

    def generate_private_key(self, length):
        private_key = [random.randint(1, 10)]
        for _ in range(1, length):
            next_value = sum(private_key) + random.randint(1, 10)
            private_key.append(next_value)
        return private_key

    def encrypt(self, pixel_values):
        binary_str = to_binary(pixel_values)
        cipher_blocks = []
        for i in range(0, len(binary_str), 8):
            chunk = binary_str[i: i + 8].ljust(8, "0")
            encrypted_sum = sum(int(bit) * self.public_key[j] for j, bit in enumerate(chunk))
            cipher_blocks.append(encrypted_sum)
        return cipher_blocks

    def decrypt(self, ciphertext):
        n_inv = modinv(self.n, self.m)
        decrypted_bits = []
        for cipher_block in ciphertext:
            c_prime = (cipher_block * n_inv) % self.m
            bits = ["0"] * len(self.private_key)
            for i in reversed(range(len(self.private_key))):
                if self.private_key[i] <= c_prime:
                    bits[i] = "1"
                    c_prime -= self.private_key[i]
            decrypted_bits.append("".join(bits))
        decrypted_binary_str = "".join(decrypted_bits)
        return to_decimal(decrypted_binary_str)

def image_to_pixels(image_path):
    image = Image.open(image_path)
    pixel_values = list(image.getdata())
    flat_pixel_values = [val for sublist in pixel_values for val in sublist]  # Flatten pixels
    return flat_pixel_values, image.size, image.mode

def pixels_to_image(pixel_values, image_size, mode):
    reshaped_pixels = [tuple(pixel_values[i:i + 3]) for i in range(0, len(pixel_values), 3)]
    image = Image.new(mode, image_size)
    image.putdata(reshaped_pixels)
    return image

def encrypted_pixels_to_image(encrypted_values, image_size):
    width, height = image_size
    # Normalize encrypted values to fit in 0-255 range
    max_value = max(encrypted_values)
    min_value = min(encrypted_values)
    normalized_values = [int((val - min_value) / (max_value - min_value) * 255) for val in encrypted_values]
    return pixels_to_image(normalized_values, image_size, "RGB")

# Main logic to encrypt and decrypt the image
knapsack = KnapsackCryptosystem()

# Load the image and convert it to pixel values
image_path = "nature.jpg"
pixel_values, image_size, mode = image_to_pixels(image_path)

# Encrypt the pixel values
ciphertext = knapsack.encrypt(pixel_values)

# Convert ciphertext to a flat list for image conversion
encrypted_image = encrypted_pixels_to_image(ciphertext, image_size)
encrypted_image.show()  # Display the encrypted image
encrypted_image.save("encrypted_image.png")  # Save the encrypted image

# Decrypt the pixel values
decrypted_pixels = knapsack.decrypt(ciphertext)

# Convert the decrypted pixel values back into an image
decrypted_image = pixels_to_image(decrypted_pixels, image_size, mode)
decrypted_image.show()  # Display the decrypted image
decrypted_image.save("decrypted_image.png")  # Save the decrypted image