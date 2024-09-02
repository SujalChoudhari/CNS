from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import time
from tabulate import tabulate

def pad(data, block_size):
    padder = padding.PKCS7(block_size).padder()
    return padder.update(data) + padder.finalize()

def unpad(padded_data, block_size):
    unpadder = padding.PKCS7(block_size).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

def encrypt_decrypt_aes_des(plaintext, key, cipher_mode, algorithm='AES'):
    block_size = 128 if algorithm == 'AES' else 64
    padded_plaintext = pad(plaintext, block_size)

    if algorithm == 'AES':
        cipher = Cipher(algorithms.AES(key), cipher_mode, backend=default_backend())
    elif algorithm == 'DES':
        cipher = Cipher(algorithms.TripleDES(key), cipher_mode, backend=default_backend())
    else:
        raise ValueError("Unsupported algorithm")

    encryptor = cipher.encryptor()
    decryptor = cipher.decryptor()

    start_time = time.time()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    encrypt_time = (time.time() - start_time) * 1000

    start_time = time.time()
    decrypted_padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    decrypted_plaintext = unpad(decrypted_padded_plaintext, block_size)
    decrypt_time = (time.time() - start_time) * 1000

    return ciphertext, encrypt_time, decrypted_plaintext, decrypt_time

def avalanche_effect(plaintext, key, mode, algorithm='AES'):
    original_ciphertext, _, _, _ = encrypt_decrypt_aes_des(plaintext, key, mode, algorithm)
    
    modified_plaintext = bytearray(plaintext)
    modified_plaintext[0] ^= 1
    modified_ciphertext, _, _, _ = encrypt_decrypt_aes_des(modified_plaintext, key, mode, algorithm)
    
    changed_bits = sum(bin(a ^ b).count('1') for a, b in zip(original_ciphertext, modified_ciphertext))
    
    return original_ciphertext, modified_ciphertext, changed_bits, plaintext, modified_plaintext

def key_change_effect(plaintext, key, mode, algorithm='AES'):
    original_ciphertext, _, _, _ = encrypt_decrypt_aes_des(plaintext, key, mode, algorithm)
    
    # Change one character in the key
    modified_key = bytearray(key)
    modified_key[0] ^= 1
    modified_ciphertext, _, _, _ = encrypt_decrypt_aes_des(plaintext, bytes(modified_key), mode, algorithm)
    
    changed_bits = sum(bin(a ^ b).count('1') for a, b in zip(original_ciphertext, modified_ciphertext))
    
    return original_ciphertext, modified_ciphertext, changed_bits, key, modified_key

def main():
    plaintext = b"12345678"
    aes_key = b"thisoneis16long#"
    des_key = b"18345678"
    aes_iv = b"0000000000000000"
    des_iv = b"00000000"
    
    aes_mode = modes.CBC(aes_iv)
    aes_ciphertext, aes_enc_time, aes_decrypted, aes_dec_time = encrypt_decrypt_aes_des(plaintext, aes_key, aes_mode, 'AES')
    
    des_mode = modes.CBC(des_iv)
    des_ciphertext, des_enc_time, des_decrypted, des_dec_time = encrypt_decrypt_aes_des(plaintext, des_key, des_mode, 'DES')
    
    aes_original_ct, aes_new_ct, aes_bits_changed, aes_orig_pt, aes_mod_pt = avalanche_effect(plaintext, aes_key, aes_mode, 'AES')
    des_original_ct, des_new_ct, des_bits_changed, des_orig_pt, des_mod_pt = avalanche_effect(plaintext, des_key, des_mode, 'DES')
    
    aes_key_original_ct, aes_key_new_ct, aes_key_bits_changed, aes_key_orig, aes_key_mod = key_change_effect(plaintext, aes_key, aes_mode, 'AES')
    des_key_original_ct, des_key_new_ct, des_key_bits_changed, des_key_orig, des_key_mod = key_change_effect(plaintext, des_key, des_mode, 'DES')
    
    encryption_decryption_times = [
        ["Algorithm", "Ciphertext", "Encryption Time (ms)", "Decryption Time (ms)"],
        ["AES", aes_ciphertext.hex(), aes_enc_time, aes_dec_time],
        ["DES", des_ciphertext.hex(), des_enc_time, des_dec_time]
    ]
    
    avalanche_effects = [
        ["Algorithm", "Original Plaintext", "Changed Plaintext", "Original Ciphertext", "New Ciphertext", "Bits Changed"],
        ["AES", aes_orig_pt.decode(), aes_mod_pt.decode(), aes_original_ct.hex(), aes_new_ct.hex(), aes_bits_changed],
        ["DES", des_orig_pt.decode(), des_mod_pt.decode(), des_original_ct.hex(), des_new_ct.hex(), des_bits_changed]
    ]
    
    key_change_effects = [
        ["Algorithm", "Original Key", "Modified Key", "Original Ciphertext", "New Ciphertext", "Bits Changed"],
        ["AES", aes_key_orig.decode(), aes_key_mod.decode(), aes_key_original_ct.hex(), aes_key_new_ct.hex(), aes_key_bits_changed],
        ["DES", des_key_orig.decode(), des_key_mod.decode(), des_key_original_ct.hex(), des_key_new_ct.hex(), des_key_bits_changed]
    ]
    
    print("Encryption and Decryption Times:")
    print(tabulate(encryption_decryption_times, headers="firstrow", tablefmt="grid"))
    
    print("\nAvalanche Effect:")
    print(tabulate(avalanche_effects, headers="firstrow", tablefmt="grid"))

    print("\nKey Change Effect:")
    print(tabulate(key_change_effects, headers="firstrow", tablefmt="grid"))

if __name__ == "__main__":
    main()