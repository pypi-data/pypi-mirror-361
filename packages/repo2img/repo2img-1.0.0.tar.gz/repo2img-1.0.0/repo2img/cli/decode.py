from PIL import Image
from core.decoder import decode_from_image
from core.crypto import decrypt
from core.archiver import unarchive_repo_zip, unarchive_repo_tar_zstd

# Disable decompression bomb check for large images
Image.MAX_IMAGE_PIXELS = None

def decode_image(args):
    """
    Handles the decoding process with minimal output.
    """
    # Magic numbers to identify the format
    MAGIC_STANDARD = b'R2IS'
    MAGIC_FAST = b'R2IF'

    processed_data = decode_from_image(args.path, quiet=getattr(args, 'quiet', True))
    
    if args.password:
        processed_data = decrypt(processed_data, args.password)

    magic_number = processed_data[:4]
    archived_data = processed_data[4:]
    
    if magic_number == MAGIC_FAST:
        unarchive_repo_tar_zstd(archived_data, args.endpath, threads=args.threads)
    elif magic_number == MAGIC_STANDARD:
        unarchive_repo_zip(archived_data, args.endpath)
    else:
        raise ValueError("Unknown or corrupted file format. Invalid magic number.")

    print(f"Decoding Completed: Repository restored to '{args.endpath}'")


