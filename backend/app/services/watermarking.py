import io
import numpy as np
from PIL import Image

def load_image_from_bytes(raw_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(raw_bytes)).convert("RGB")

def save_image_to_bytes(image: Image.Image, format_hint: str = "png") -> io.BytesIO:
    buf = io.BytesIO()
    # LSB requires lossless (PNG). If JPEG is passed, we force PNG for the watermark to survive
    save_format = "PNG" if "png" in format_hint.lower() or "jpg" in format_hint.lower() or "jpeg" in format_hint.lower() else "PNG"
    image.save(buf, format=save_format)
    buf.seek(0)
    return buf

def embed_watermark_lsb(image: Image.Image, watermark_text: str, strength: int = 5):
    """Embeds text into LSB. 'strength' here acts as a redundancy multiplier."""
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    data = watermark_text + "@@@@"
    # Convert string to binary string
    binary_data = ''.join(format(ord(i), '08b') for i in data)
    
    # Simple redundancy based on strength
    binary_data = binary_data * strength 
    
    # Convert image to numpy array for fast processing
    img_array = np.array(image)
    flat_array = img_array.flatten()
    
    total_pixels = flat_array.size
    
    if len(binary_data) > total_pixels:
        raise ValueError(f"Image too small for this strength/text. Need {len(binary_data)} bits but only have {total_pixels} channels.")

    # Convert binary data to numpy array of integers (0 or 1)
    bits = np.array([int(b) for b in binary_data], dtype=np.uint8)
    
    # Vectorized embedding:
    # 1. Clear LSB of target pixels (bitwise AND with 0xFE / 254)
    # 2. Set LSB to data bit (bitwise OR)
    target_slice = flat_array[:len(bits)]
    target_slice[:] = (target_slice & 0xFE) | bits
    
    # Update the flat array with modified slice (done in-place above via slicing, but confirming)
    flat_array[:len(bits)] = target_slice
    
    # Reshape back to image dimensions
    reshaped_array = flat_array.reshape(img_array.shape)
    
    # Create new image from array
    watermarked_image = Image.fromarray(reshaped_array.astype('uint8'), 'RGB')
    
    return watermarked_image, binary_data

def extract_watermark_lsb(image: Image.Image):
    """Extracts bits and looks for the @@@@ delimiter."""
    # Ensure image is in RGB mode (same as embedding)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Use numpy for fast reading
    img_array = np.array(image)
    flat_array = img_array.flatten()
    
    # Limit to first 15000 values (5000 pixels * 3 channels) for performance 
    # (Matches previous logic's 5000 pixel limit, but now parallelized reading)
    search_limit = 15000
    if flat_array.size > search_limit:
        extract_slice = flat_array[:search_limit]
    else:
        extract_slice = flat_array
        
    # Vectorized extraction: Get LSBs
    lsb_bits = extract_slice & 1
    
    # Convert to string
    binary_data = "".join(lsb_bits.astype(str))
    
    # Try to decode
    # Split into 8-bit chunks
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded = ""
    
    for b in all_bytes:
        if len(b) == 8:
            try:
                char = chr(int(b, 2))
                decoded += char
                if "@@@@" in decoded:
                    final_text = decoded.split("@@@@")[0]
                    return final_text, 1.0 # Match ratio 1.0 for found
            except:
                continue
            
    return "Unknown", 0.1 # Match ratio 0.1 for not found

def strip_metadata_from_image(image: Image.Image) -> Image.Image:
    """
    Removes all metadata and EXIF data from the image.
    Returns a clean image with only pixel data preserved.
    Preserves image format and converts to RGB if needed.
    """
    # Create a new image with only pixel data
    # This removes all metadata, EXIF, encoding information, etc.
    # Using numpy is straightforward
    data = np.array(image)
    image_without_metadata = Image.fromarray(data)
    
    return image_without_metadata
