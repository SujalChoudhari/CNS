import socket
import threading
import random
from Crypto.Util.number import isPrime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# ANSI color codes
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"

def is_primitive_root(g, p):
    phi = p - 1
    factors = set()
    i = 2
    while i * i <= phi:
        if phi % i == 0:
            factors.add(i)
            while phi % i == 0:
                phi //= i
        i += 1
    if phi > 1:
        factors.add(phi)
    return all(pow(g, (p - 1) // factor, p) != 1 for factor in factors)

def generate_keypair(p, g):
    private_key = random.randint(1, p - 1)
    public_key = pow(g, private_key, p)
    return private_key, public_key

def calculate_shared_secret(private_key, other_public_key, p):
    return pow(other_public_key, private_key, p)

def generate_rsa_key(shared_secret):
    random.seed(shared_secret)
    return RSA.generate(2048)

def encrypt_message(message, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(message.encode())

def decrypt_message(encrypted_message, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(encrypted_message).decode()

def receive_messages(sock, private_key):
    while True:
        try:
            encrypted_message = sock.recv(1024)
            if not encrypted_message:
                break
            decrypted_message = decrypt_message(encrypted_message, private_key)
            print(f"{GREEN}[INFO]: Received (decrypted): {decrypted_message}{RESET}")
        except Exception as e:
            print(f"{RED}[INFO]: Error receiving message: {e}{RESET}")
            break

def server():
    host = input(f"{YELLOW}[INFO]: Enter the IP address of the Client: {RESET}")
    port = 54321

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))
    print(f"{GREEN}[INFO]: Connected to Client at {host}:{port}{RESET}")

    p = int(input(f"{YELLOW}[INPUT]: Enter the same prime number p as the Client: {RESET}"))
    while not isPrime(p):
        p = int(input(f"{YELLOW}[INPUT]: The number is not prime. Please enter a valid prime number p: {RESET}"))

    g, client_public_key = map(int, server_socket.recv(1024).decode().split(',')[1:])
    print(f"{GREEN}[INFO]: Received Generator g: {g}{RESET}")
    print(f"{GREEN}[INFO]: Received Diffie-Hellman Public Key from Client: {client_public_key}{RESET}")

    if not is_primitive_root(g, p):
        print(f"{RED}Error: {g} is not a primitive root of {p}.{RESET}")
        server_socket.close()
        return

    private_key, public_key = generate_keypair(p, g)
    print(f"{BLUE}[INFO]: Private Key: {private_key}{RESET}")
    print(f"{BLUE}[INFO]: Public Key: {public_key}{RESET}")

    server_socket.send(str(public_key).encode())

    shared_secret = calculate_shared_secret(private_key, client_public_key, p)
    print(f"{BLUE}[INFO]: Shared Secret: {shared_secret}{RESET}")

    rsa_key = generate_rsa_key(shared_secret)
    print(f"{GREEN}[INFO]: RSA Key Pair Generated{RESET}")

    client_rsa_public_key = RSA.import_key(server_socket.recv(1024))
    server_socket.send(rsa_key.publickey().export_key())
    print(f"{GREEN}[INFO]: RSA Public Keys Exchanged{RESET}")

    receive_thread = threading.Thread(target=receive_messages, args=(server_socket, rsa_key))
    receive_thread.start()

    while True:
        message = input(f"{YELLOW}[INFO]: Enter message to send (or 'q' to quit): {RESET}")
        if message.lower() == 'q':
            break
        encrypted_message = encrypt_message(message, client_rsa_public_key)
        server_socket.send(encrypted_message)
        print(f"{GREEN}[INFO]: Sent (encrypted): {encrypted_message.hex()}{RESET}")

    server_socket.close()

if __name__ == "__main__":
    server()