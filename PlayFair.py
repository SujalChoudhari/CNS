from pprint import pprint


def generate_matrix(key: str) -> list[list[str]]:
    key = "".join(sorted(set(key.upper()), key=key.index))
    available_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    seed_matrix = []
    used_chars = set()

    for char in key:
        if char in available_chars and char not in used_chars:
            used_chars.add(char)
            seed_matrix.append(char)

    for char in available_chars:
        if char not in used_chars:
            used_chars.add(char)
            seed_matrix.append(char)

    matrix = []
    for i in range(5):
        matrix.append(seed_matrix[i * 6 : (i + 1) * 6])

    return matrix


def encrypt_playfair(matrix: list[list[str]], plaintext: str) -> str:
    lookup = {
        char: (i, j) for i, row in enumerate(matrix) for j, char in enumerate(row)
    }

    plaintext = plaintext.upper().replace("J", "I").replace(" ", "")
    digraphs = []

    i = 0
    while i < len(plaintext):
        char1 = plaintext[i]
        if i + 1 < len(plaintext):
            char2 = plaintext[i + 1]
            if char1 == char2:
                digraphs.append(char1 + "X")
                i += 1
            else:
                digraphs.append(char1 + char2)
                i += 2
        else:
            digraphs.append(char1 + "X")
            i += 1

    ciphertext = []

    for digraph in digraphs:
        row1, col1 = lookup[digraph[0]]
        row2, col2 = lookup[digraph[1]]

        if row1 == row2:
            ciphertext.append(matrix[row1][(col1 + 1) % 6])
            ciphertext.append(matrix[row2][(col2 + 1) % 6])
        elif col1 == col2:
            ciphertext.append(matrix[(row1 + 1) % 5][col1])
            ciphertext.append(matrix[(row2 + 1) % 5][col2])
        else:
            ciphertext.append(matrix[row1][col2])
            ciphertext.append(matrix[row2][col1])

    return "".join(ciphertext)

def decrypt_playfair(matrix: list[list[str]], ciphertext: str) -> str:
    lookup = {
        char: (i, j) for i, row in enumerate(matrix) for j, char in enumerate(row)
    }

    digraphs = []
    i = 0
    while i < len(ciphertext):
        char1 = ciphertext[i]
        char2 = ciphertext[i + 1] if i + 1 < len(ciphertext) else 'X'
        digraphs.append(char1 + char2)
        i += 2

    plaintext = []

    for digraph in digraphs:
        row1, col1 = lookup[digraph[0]]
        row2, col2 = lookup[digraph[1]]

        if row1 == row2:
            plaintext.append(matrix[row1][(col1 - 1) % 6])
            plaintext.append(matrix[row2][(col2 - 1) % 6])
        elif col1 == col2:
            plaintext.append(matrix[(row1 - 1) % 5][col1])
            plaintext.append(matrix[(row2 - 1) % 5][col2])
        else:
            plaintext.append(matrix[row1][col2])
            plaintext.append(matrix[row2][col1])

    return ''.join(plaintext).replace("X", "").rstrip()

if __name__ == "__main__":
    key = "TODAY123"
    plaintext = "ATTACKTONIGHT"
    matrix: list = generate_matrix(key)
    encrypted_text = encrypt_playfair(matrix, plaintext)
    decrypted_text = decrypt_playfair(matrix, encrypted_text)

    pprint(matrix)
    print("Encrypted Text:", encrypted_text)
    print("Decrypted Text:", decrypted_text)
