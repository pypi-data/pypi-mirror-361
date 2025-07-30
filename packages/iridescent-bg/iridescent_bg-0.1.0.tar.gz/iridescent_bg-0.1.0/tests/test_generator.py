# tests/test_generator.py

import unittest
from PIL import Image
from iridescent_bg import generate_iridescent_background

class TestIridescentBackground(unittest.TestCase):
    def test_generate_background(self):
        # Test default parameters
        bg = generate_iridescent_background()
        self.assertIsInstance(bg, Image.Image)
        self.assertEqual(bg.size, (1080, 1080))
        self.assertEqual(bg.mode, "RGBA")

    def test_custom_parameters(self):
        # Test custom dimensions and parameters
        bg = generate_iridescent_background(width=500, height=500, splash_count=10,
                                          splash_opacity=50, splash_blur=10, dash_length=100)
        self.assertEqual(bg.size, (500, 500))
        self.assertEqual(bg.mode, "RGBA")

    def test_base_color(self):
        # Test custom base color
        bg = generate_iridescent_background(base_color="white")
        self.assertEqual(bg.getpixel((0, 0))[:3], (255, 255, 255))  # Check base color

if __name__ == "__main__":
    unittest.main()
