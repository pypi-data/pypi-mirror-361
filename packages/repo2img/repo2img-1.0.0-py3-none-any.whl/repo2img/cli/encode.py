import os
import math
from core.archiver import archive_repo_zip, archive_repo_tar_zstd
from core.crypto import encrypt
from core.encoder import encode_to_image

def get_human_readable_size(size_bytes):
    """Converts a size in bytes to a human-readable string."""
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def encode_repo(args):
    """
    Handles the encoding process with minimal output.
    """
    if not args.fast:
        archived_data = archive_repo_zip(args.path)
        magic_number = b'R2IS'
    else:
        archived_data = archive_repo_tar_zstd(args.path, threads=args.threads)
        magic_number = b'R2IF'

    data_to_process = magic_number + archived_data
    
    if args.encrypt:
        if not args.password:
            raise ValueError("Password is required for encryption.")
        data_to_process = encrypt(data_to_process, args.password)
        
    encode_to_image(data_to_process, args.out, quiet=getattr(args, 'quiet', True))
    
    try:
        file_size = os.path.getsize(args.out)
        print(f"Encoding Completed: Image created at '{args.out}' (Size: {get_human_readable_size(file_size)})")
    except FileNotFoundError:
        print(f"Error: Output file '{args.out}' not found after encoding.")

