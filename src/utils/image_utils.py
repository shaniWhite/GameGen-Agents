
import base64

def encode_image_to_base64(image_path):
    """Encodes an image to base64 format."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding {image_path}: {e}")
        return None