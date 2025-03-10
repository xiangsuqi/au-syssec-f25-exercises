from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def decrypt_with_private_key(pem_file, hex_ciphertext):
    # Read the private key from the PEM file
    with open(pem_file, 'r') as f:
        private_key = RSA.import_key(f.read())
    
    # Initialize the cipher with PKCS1_OAEP
    cipher = PKCS1_OAEP.new(private_key)
    
    # Convert hex ciphertext to bytes
    ciphertext_bytes = bytes.fromhex(hex_ciphertext)
    
    # Decrypt the ciphertext
    plaintext = cipher.decrypt(ciphertext_bytes)
    
    return plaintext.decode()

# Example usage
pem_file_path = "private.pem"
ciphertext_hex = "your_hex_ciphertext_here"  # Replace with actual hex-encoded ciphertext

decrypted_message = decrypt_with_private_key(pem_file_path, ciphertext_hex)
print("Decrypted Message:", decrypted_message)
