import os
import tarfile
import zipfile
from io import BytesIO
import zstandard as zstd

def archive_repo_zip(path: str) -> bytes:
    """Archives a repository into a zip file in memory (standard method)."""
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        all_files = sorted([os.path.join(root, file) for root, _, files in os.walk(path) for file in files])
        for file_path in all_files:
            arcname = os.path.relpath(file_path, path)
            zf.write(file_path, arcname)
    memory_file.seek(0)
    return memory_file.read()

def unarchive_repo_zip(data: bytes, out_path: str):
    """Unarchives a repository from a zip file in memory."""
    with zipfile.ZipFile(BytesIO(data), 'r') as zf:
        zf.extractall(out_path)

def archive_repo_tar_zstd(path: str, threads: int = -1) -> bytes:
    """
    Archives a repository using tar and compresses it with zstandard in memory.
    """
    tar_stream = BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        all_files = sorted([os.path.join(root, file) for root, _, files in os.walk(path) for file in files])
        for file_path in all_files:
            arcname = os.path.relpath(file_path, path)
            tar.add(file_path, arcname=arcname)
    tar_stream.seek(0)
    
    cctx = zstd.ZstdCompressor(threads=threads)
    return cctx.compress(tar_stream.read())

def unarchive_repo_tar_zstd(data: bytes, out_path: str, threads: int = -1):
    """
    Decompresses zstandard data and unarchives it from tar in memory.
    """
    dctx = zstd.ZstdDecompressor()
    decompressed_data = dctx.decompress(data)
    
    with tarfile.open(fileobj=BytesIO(decompressed_data), mode='r') as tar:
        tar.extractall(path=out_path)

