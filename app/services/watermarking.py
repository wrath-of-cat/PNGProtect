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
    data = watermark_text + "@@@@"
    binary_data = ''.join(format(ord(i), '08b') for i in data)
    
    # Simple redundancy based on strength
    binary_data = binary_data * strength 
    
    pixels = np.array(image)
    flat = pixels.flatten()
    
    if len(binary_data) > len(flat):
        raise ValueError("Image too small for this strength/text.")

    for i in range(len(binary_data)):
        flat[i] = (flat[i] & ~1) | int(binary_data[i])
        
    return Image.fromarray(flat.reshape(pixels.shape).astype('uint8')), binary_data

def extract_watermark_lsb(image: Image.Image):
    """Extracts bits and looks for the @@@@ delimiter."""
    pixels = np.array(image)
    flat = pixels.flatten()
    
    binary_data = "".join([str(flat[i] & 1) for i in range(min(len(flat), 16000))])
    
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded = ""
    for b in all_bytes:
        try:
            char = chr(int(b, 2))
            decoded += char
            if "@@@@" in decoded:
                final_text = decoded.split("@@@@")[0]
                return final_text, 1.0 # Match ratio 1.0 for found
        except:
            continue
            
    return "Unknown", 0.1 # Match ratio 0.1 for not found