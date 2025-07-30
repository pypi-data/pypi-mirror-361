import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
PBKDF2_ITERATIONS = 100_000

def get_key(password: str, salt: bytes) -> bytes:
    """Derives a key from the password and salt using PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt(data: bytes, password: str) -> bytes:
    """
    Encrypts data with AES-256-GCM using a derived key.
    """
    salt = os.urandom(SALT_SIZE)
    key = get_key(password, salt)
    
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    return salt + nonce + ciphertext

def decrypt(data: bytes, password: str) -> bytes:
    """
    Decrypts data with AES-256-GCM using a derived key.
    """
    try:
        salt = data[:SALT_SIZE]
        nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        ciphertext = data[SALT_SIZE + NONCE_SIZE:]

        key = get_key(password, salt)
        
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed. Check password or data integrity. Error: {e}")

