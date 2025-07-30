# iridescent_bg/generator.py

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import colorsys
import os

def generate_iridescent_background(width=1080, height=1080, splash_count=75,
                                 splash_opacity=100, splash_blur=20, dash_length=200,
                                 base_color="black", enhance_vibrancy=False, full_canvas=True):
    """
    Generate an iridescent background with random colored lines and Gaussian blur.

    Args:
        width (int): Width of the output image (default: 1080).
        height (int): Height of the output image (default: 1080).
        splash_count (int): Number of random lines (default: 75).
        splash_opacity (int): Opacity of lines (0-255, default: 100).
        splash_blur (float): Gaussian blur radius (default: 20).
        dash_length (int): Maximum length of random lines (default: 200).
        base_color (str): Background color (default: "black", supports PIL color names or hex e.g., '#FFFFFF').
        enhance_vibrancy (bool): Increase saturation and line width for a more striking effect (default: False).
        full_canvas (bool): Apply background to full canvas with RGB conversion (default: True).

    Returns:
        PIL.Image: RGB image with iridescent background.
    """
    bg = Image.new("RGBA", (width, height), base_color)
    d = ImageDraw.Draw(bg)
    for _ in range(splash_count):
        x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
        x2 = np.clip(x1 + np.random.randint(-dash_length, dash_length), 0, width)
        y2 = np.clip(y1 + np.random.randint(-dash_length, dash_length), 0, height)
        hue = np.random.random()
        sat = 0.8 + 0.1 * np.random.random() if enhance_vibrancy else 0.5 + 0.3 * np.random.random()
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, sat, 1)]
        line_width = np.random.randint(5, 25) if enhance_vibrancy else np.random.randint(5, 20)
        d.line((x1, y1, x2, y2), fill=(r, g, b, splash_opacity), width=line_width)
    result = bg.filter(ImageFilter.GaussianBlur(splash_blur))
    return result.convert("RGB") if full_canvas else result

def add_text(image, text="Sample Text", font_size=40, font_color="white", position=(0, 0), 
             center_top=False, font_paths=None):
    """
    Add text to the image with optional centering at the top.

    Args:
        image (PIL.Image): Image to add text to.
        text (str): Text to add (default: "Sample Text").
        font_size (int): Font size in points (default: 40).
        font_color (str): Text color (default: "white", supports PIL color names or hex).
        position (tuple): (x, y) coordinates for text (default: (0, 0)).
        center_top (bool): Center text horizontally at the top (y=20) if True (default: False).
        font_paths (list): List of font file paths to try (default: None, uses default font).

    Returns:
        PIL.Image: Image with added text.
    """
    draw = ImageDraw.Draw(image)
    if font_paths is None:
        font_paths = ["/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()
    if center_top:
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        x = (image.width - text_width) // 2
        y = 20
        position = (x, y)
    draw.text(position, text, fill=font_color, font=font)
    return image

def add_image(image, side_image_path=None, width=540, position=(0, 0), aspect_ratio=None):
    """
    Add an optional side image to the background with customizable position.

    Args:
        image (PIL.Image): Background image.
        side_image_path (str): Path to the side image file (default: None).
        width (int): Desired width of the side image (default: 540).
        position (tuple): (x, y) coordinates for the image (default: (0, 0)).
        aspect_ratio (float): Optional aspect ratio to override image's natural ratio (default: None).

    Returns:
        PIL.Image: Image with added side image, or original if no path provided.
    """
    if side_image_path:
        side_img = Image.open(side_image_path).convert("RGB")
        if aspect_ratio is None:
            aspect_ratio = side_img.width / side_img.height
        height = int(width / aspect_ratio)
        side_img_resized = side_img.resize((width, height), Image.LANCZOS)
        # Center vertically in the lane if height allows
        y_offset = (image.height - height) // 2 if position[0] == 0 else position[1]
        image.paste(side_img_resized, (position[0], y_offset))
    return image
