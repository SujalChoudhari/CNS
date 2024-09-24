import numpy as np
import random


def to_binary(ascii_values):
    binary_str = "".join(format(val, "08b") for val in ascii_values)
    return binary_str


def to_ascii(binary_str):
    ascii_values = [int(binary_str[i : i + 8], 2) for i in range(0, len(binary_str), 8)]
    return "".join(chr(val) for val in ascii_values)


def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1


class KnapsackCryptosystem:
    def __init__(self, length=6):
        self.private_key = self.generate_private_key(length)
        self.m = sum(self.private_key) + random.randint(
            10, 20
        )  # everytime a new private key is generated
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

    def encrypt(self, plaintext):
        ascii_values = [ord(c) for c in plaintext]
        binary_str = to_binary(ascii_values)
        print(f"{ascii_values = }")
        print(f"{binary_str = }")

        cipher_blocks = []
        for i in range(0, len(binary_str), 6):
            chunk = binary_str[i : i + 6]
            chunk = chunk.ljust(6, "0")
            encrypted_sum = sum(
                int(bit) * self.public_key[j] for j, bit in enumerate(chunk)
            )
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

        print(f"{decrypted_bits = }")

        decrypted_binary_str = "".join(decrypted_bits)
        print(f"{decrypted_binary_str = }")
        return to_ascii(decrypted_binary_str)


knapsack = KnapsackCryptosystem()

plaintext = "Testing a very looong message"
print("Original Plaintext:", plaintext)

ciphertext = knapsack.encrypt(plaintext)
print("Ciphertext:", ciphertext)

decrypted_text = knapsack.decrypt(ciphertext)
print("Decrypted Text:", decrypted_text)
