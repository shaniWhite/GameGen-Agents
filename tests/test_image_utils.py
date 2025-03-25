
import unittest
import os
import base64
import numpy as np
import cv2
from src.utils import image_utils  

class TestEncodeImageToBase64(unittest.TestCase):

    def setUp(self):
        self.image_path = "tests/test_image.png"
        os.makedirs("tests", exist_ok=True)

        # Create a simple black square image
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(self.image_path, img)

    def tearDown(self):
        if os.path.exists(self.image_path):
            os.remove(self.image_path)

    def test_encode_image_success(self):
        result = image_utils.encode_image_to_base64(self.image_path)
        self.assertIsInstance(result, str)
        decoded = base64.b64decode(result)
        self.assertGreater(len(decoded), 0)

    def test_encode_image_file_not_found(self):
        result = image_utils.encode_image_to_base64("nonexistent.png")
        self.assertIsNone(result)
