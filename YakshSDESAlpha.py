import random

# Permutation Tables and S-Boxes
PermutationP10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
PermutationP8 = [6, 3, 7, 4, 8, 5, 10, 9]
Initial_Permutation_IP = [2, 6, 3, 1, 4, 8, 5, 7]
Expanded_Permutation_EP = [4, 1, 2, 3, 2, 3, 4, 1]
PermutationP4 = [2, 4, 3, 1]
Inverse_of_Inital_Permutation_IP_inv = [4, 1, 3, 5, 7, 2, 8, 6]
S_Box_0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
S_Box_1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]

# Variables to store generated 8-bit keys
key1_8bits = [0] * 8
key2_8bits = [0] * 8

def binary(value, bits=8):
    return format(value, f'0{bits}b')

def swap_bits(arr, size):
    left = arr[:size]
    right = arr[size:]
    return right + left

def binary_to_decimal(bits):
    return int(''.join(map(str, bits)), 2)

def permute(bits, table):
    return [bits[i - 1] for i in table]

def function_(bits, key):
    left_4bits = bits[:4]
    right_4bits = bits[4:]

    ep = permute(right_4bits, Expanded_Permutation_EP)
    xor_result = [ep[i] ^ key[i] for i in range(8)]

    left_4bits_1 = xor_result[:4]
    right_4bits_1 = xor_result[4:]

    row = binary_to_decimal([left_4bits_1[0], left_4bits_1[3]])
    column = binary_to_decimal([left_4bits_1[1], left_4bits_1[2]])
    value = S_Box_0[row][column]
    str_left = [int(x) for x in binary(value, 2)]

    row = binary_to_decimal([right_4bits_1[0], right_4bits_1[3]])
    column = binary_to_decimal([right_4bits_1[1], right_4bits_1[2]])
    value = S_Box_1[row][column]
    str_right = [int(x) for x in binary(value, 2)]

    r_ = str_left + str_right
    r_p4 = permute(r_, PermutationP4)
    left_4bits = [left_4bits[i] ^ r_p4[i] for i in range(4)]

    return left_4bits + right_4bits

def decryption_of_ciphertext(ciphertext_binary):
    tmp = permute(ciphertext_binary, Initial_Permutation_IP)
    print("Decryption - After Initial Permutation:", ''.join(map(str, tmp)))

    arr1 = function_(tmp, key2_8bits)
    print("Decryption - After Function with Key2:", ''.join(map(str, arr1)))
    after_swap = swap_bits(arr1, len(arr1) // 2)
    print("Decryption - After Swap:", ''.join(map(str, after_swap)))

    arr2 = function_(after_swap, key1_8bits)
    print("Decryption - After Function with Key1:", ''.join(map(str, arr2)))

    return permute(arr2, Inverse_of_Inital_Permutation_IP_inv)

def encryption_of_plaintext(plaintext_binary):
    tmp = permute(plaintext_binary, Initial_Permutation_IP)
    print("Encryption - After Initial Permutation:", ''.join(map(str, tmp)))

    arr1 = function_(tmp, key1_8bits)
    print("Encryption - After Function with Key1:", ''.join(map(str, arr1)))
    after_swap = swap_bits(arr1, len(arr1) // 2)
    print("Encryption - After Swap:", ''.join(map(str, after_swap)))

    arr2 = function_(after_swap, key2_8bits)
    print("Encryption - After Function with Key2:", ''.join(map(str, arr2)))

    return permute(arr2, Inverse_of_Inital_Permutation_IP_inv)

def decimal_to_binary(decimal):
    return [int(x) for x in format(decimal, '08b')]

def shift(binary, n):
    return binary[n:] + binary[:n]

def key_generation(key_10bit):
    key_ = permute(key_10bit, PermutationP10)
    left_side = key_[:5]
    right_side = key_[5:]

    left_shift1 = shift(left_side, 1)
    right_shift1 = shift(right_side, 1)
    key_1 = left_shift1 + right_shift1
    global key1_8bits
    key1_8bits = permute(key_1, PermutationP8)

    left_shift2 = shift(left_side, 2)
    right_shift2 = shift(right_side, 2)
    key_2 = left_shift2 + right_shift2
    global key2_8bits
    key2_8bits = permute(key_2, PermutationP8)

    print(f"Generated 8-Bit Key1 (K1): {''.join(map(str, key1_8bits))}")
    print(f"Generated 8-Bit Key2 (K2): {''.join(map(str, key2_8bits))}")

def generate_random_key(size_of_key):
    return [random.randint(0, 1) for _ in range(size_of_key)]

def solve():
    key_10bit = generate_random_key(10)

    print(f"Generated 10-Bit Key: {''.join(map(str, key_10bit))}")

    key_generation(key_10bit)

    plaintext = input("Enter Message: ")
    print(f"Plaintext: {''.join(map(str, decimal_to_binary(ord(plaintext[0]))))}")

    cipher_text = []
    for char in plaintext:
        binary_of_plaintext = decimal_to_binary(ord(char))
        print(f"Original Binary of '{char}': {''.join(map(str, binary_of_plaintext))}")
        cipher_text_8bits = encryption_of_plaintext(binary_of_plaintext)
        print(f"Encrypted Binary of '{char}': {''.join(map(str, cipher_text_8bits))}")
        ct = binary_to_decimal(cipher_text_8bits)
        cipher_text.append(ct)

    print(f"Ciphertext: {''.join(map(str, cipher_text_8bits))}")

    decrypted_text = ''
    for ct in cipher_text:
        cipher_text_8bits = decimal_to_binary(ct)
        decrypted_8bits = decryption_of_ciphertext(cipher_text_8bits)
        decrypted_text += chr(binary_to_decimal(decrypted_8bits))

    print(f"Decrypted Plaintext: {decrypted_text}")

if __name__ == "__main__":
    solve()
