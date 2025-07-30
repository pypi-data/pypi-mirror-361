import argparse
import os
from .cli.encode import encode_repo
from .cli.decode import decode_image

def main():
    parser = argparse.ArgumentParser(
        description="A high-performance CLI tool to convert a code repository into a single, compressed, and encrypted PNG image and back.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Encode Command ---
    enc = subparsers.add_parser(
        "encode", 
        help="Encode a repository folder into a single image file.",
        description="Usage: python main.py encode --path ./my_repo --out repo.png"
    )
    enc.add_argument("--path", required=True, help="Path to the source repository folder.")
    enc.add_argument("--out", required=True, help="Path for the output image file (e.g., 'my_repo.png').")
    enc.add_argument("--encrypt", action="store_true", help="Enable AES-256 encryption.")
    enc.add_argument("--password", type=str, default=None, help="Password for encryption. Required if --encrypt is used.")
    enc.add_argument('--fast', default=True, action=argparse.BooleanOptionalAction, help="Use fast zstd compression (default: enabled). Use --no-fast for standard zip.")
    enc.add_argument("--threads", type=int, default=os.cpu_count(), help=f"Number of threads for compression (default: {os.cpu_count()}).")

    # --- Decode Command ---
    dec = subparsers.add_parser(
        "decode", 
        help="Decode an image file back into a repository folder.",
        description="Usage: python main.py decode --path repo.png --endpath ./restored_repo"
    )
    dec.add_argument("--path", required=True, help="Path to the input image file.")
    dec.add_argument("--endpath", required=True, help="Directory where the repository will be restored.")
    dec.add_argument("--password", type=str, default=None, help="Password for decryption. Required if the image was encrypted.")
    dec.add_argument("--threads", type=int, default=os.cpu_count(), help=f"Number of threads for decompression (default: {os.cpu_count()}).")

    args = parser.parse_args()

    # Add a 'quiet' flag to the args namespace for the handlers to use
    # This is a simple way to control verbosity without adding it to every subparser
    args.quiet = False # You could make this a real argument later if needed

    if args.command == "encode":
        encode_repo(args)
    elif args.command == "decode":
        decode_image(args)
    else:
        # This part is now redundant because of `required=True` in subparsers
        parser.print_help()

if __name__ == "__main__":
    main()

