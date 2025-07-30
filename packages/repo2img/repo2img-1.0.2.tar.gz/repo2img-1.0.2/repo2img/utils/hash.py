import hashlib

def get_sha256(data):
    """
    Calculates the SHA256 hash of a byte string.
    """
    return hashlib.sha256(data).hexdigest()
