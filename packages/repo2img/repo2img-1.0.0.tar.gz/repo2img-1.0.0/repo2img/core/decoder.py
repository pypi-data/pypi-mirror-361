import numpy as np
from PIL import Image
import struct
import time

def decode_from_image(image_path: str, **kwargs) -> bytes:
    """
    Decodes a Grayscale PNG image back to a byte string.
    """
    img = Image.open(image_path)
    if img.mode != 'L':
        img = img.convert('L')
        
    pixels = np.array(img)
    data = pixels.tobytes()
    
    header_size = struct.calcsize('>Q')
    if len(data) < header_size:
        raise ValueError("Data is too short to contain a valid header.")
    original_length = struct.unpack('>Q', data[:header_size])[0]
    
    start_of_data = header_size
    end_of_data = start_of_data + original_length
    
    if len(data) < end_of_data:
        raise ValueError("Data is corrupted or incomplete.")
        
    data = data[start_of_data:end_of_data]
    
    return data

