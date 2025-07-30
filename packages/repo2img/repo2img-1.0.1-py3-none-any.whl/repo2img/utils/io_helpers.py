import os

def get_all_files(path):
    """
    Gets all file paths in a directory.
    """
    all_files = []
    for root, _, files in os.walk(path):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

def read_file_bytes(file_path):
    """
    Reads a file and returns its content as bytes.
    """
    with open(file_path, "rb") as f:
        return f.read()

def write_file_bytes(file_path, data):
    """
    Writes bytes to a file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(data)
