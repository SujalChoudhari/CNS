from PIL import Image
import matplotlib.pyplot as plt

class ShiftCypher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, para):
        return "".join([chr((ord(x) + self.key) % 128) for x in para])

    def decrypt(self, encrypted):
        return "".join([chr((ord(x) - self.key) % 128) for x in encrypted])


class ShiftCypherInts:
    def __init__(self, key):
        self.key = key

    def process_pixel(self, pixel, operation):
        r, g, b = pixel
        bw = r + g + b % 256 * 3
        if operation == 'encrypt':
            return ((r + self.key) % 256, (r + self.key) % 256, (r + self.key) % 256)
        elif operation == 'decrypt':
            return ((r - self.key) % 256, (r - self.key) % 256, (r - self.key) % 256)
        else:
            raise ValueError("Operation must be 'encrypt' or 'decrypt'.")

    def encrypt(self, pixel):
        return self.process_pixel(pixel, 'encrypt')

    def decrypt(self, pixel):
        return self.process_pixel(pixel, 'decrypt')


def ascii_cypher():
    key = int(input("Enter Key: "))
    cypher = ShiftCypher(key)

    para = input("Enter Text: ")
    encrypted = cypher.encrypt(para).upper()
    print(f"Encrypted: {encrypted}")
    decrypted = cypher.decrypt(encrypted).lower()
    print(f"Decrypted: {decrypted}")


def apply_cipher(image, key, operation):
    cypher = ShiftCypherInts(key)
    pixels = list(image.getdata())
    if operation == 'encrypt':
        new_pixels = [cypher.encrypt(pixel) for pixel in pixels]
    elif operation == 'decrypt':
        new_pixels = [cypher.decrypt(pixel) for pixel in pixels]
    else:
        raise ValueError("Operation must be 'encrypt' or 'decrypt'.")

    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    return new_image


def show_images(original, encrypted, decrypted):
    # Create a matplotlib figure
    plt.figure(figsize=(15, 5))

    # Original Image
    plt.subplot(1, 3, 1)
    plt.imshow(original)
    plt.title("Original Image")
    plt.axis('off')  # Hide axes

    # Encrypted Image
    plt.subplot(1, 3, 2)
    plt.imshow(encrypted)
    plt.title("Encrypted Image")
    plt.axis('off')  # Hide axes

    # Decrypted Image
    plt.subplot(1, 3, 3)
    plt.imshow(decrypted)
    plt.title("Decrypted Image")
    plt.axis('off')  # Hide axes

    # Show the plot
    plt.tight_layout()
    plt.show()
    print("Images Visible")


def image_cypher():
    key = int(input("Enter Key: "))
    try:
        original_image = Image.open("nature.jpg")
    except FileNotFoundError:
        print("Error: The image file 'nature.jpg' was not found.")
        return

    encrypted_image = apply_cipher(original_image, key, 'encrypt')
    decrypted_image = apply_cipher(encrypted_image, key, 'decrypt')

    encrypted_image.save("encrypted_image.jpg")
    decrypted_image.save("decrypted_image.jpg")
    print("Images have been processed and saved.")

    # Show images using matplotlib
    show_images(original_image, encrypted_image, decrypted_image)


if __name__ == "__main__":
    # Uncomment the line below to run ASCII cipher
    # ascii_cypher()
    image_cypher()