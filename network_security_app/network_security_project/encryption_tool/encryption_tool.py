import cryptography
from cryptography.fernet import Fernet

# Encrypt and decrypt data
def encrypt(data, key):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(data.encode())
    return cipher_text

def decrypt(data, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(data)
    return plain_text.decode()

if __name__ == '__main__':
    # Generate a key
    key = Fernet.generate_key()
    
    # Example usage
    data = 'Hello, World!'
    encrypted_data = encrypt(data, key)
    decrypted_data = decrypt(encrypted_data, key)
    print(decrypted_data)