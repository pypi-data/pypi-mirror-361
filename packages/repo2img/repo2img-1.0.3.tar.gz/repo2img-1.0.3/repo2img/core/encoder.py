import numpy as np
from PIL import Image
import struct
import math
import time

def encode_to_image(data: bytes, out_path: str, **kwargs):
    """
    Encodes a byte string into a Grayscale PNG image.
    """
    data_with_len = struct.pack('>Q', len(data)) + data
    
    pixels_flat = np.frombuffer(data_with_len, dtype=np.uint8)

    num_pixels = len(pixels_flat)
    width = int(math.ceil(math.sqrt(num_pixels)))
    height = int(math.ceil(num_pixels / width))
    
    image_pixels = np.zeros(height * width, dtype=np.uint8)
    image_pixels[:num_pixels] = pixels_flat
    image_pixels = image_pixels.reshape((height, width))
    
    img = Image.fromarray(image_pixels, 'L')
    img.save(out_path, 'PNG', optimize=True, compress_level=9)


