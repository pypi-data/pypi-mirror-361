# Iridescent-BG: Vibrant Background Generator

## Overview
The `iridescent-bg` Python package generates stunning iridescent backgrounds for images, characterized by a shimmering, rainbow-like effect. Using random colored lines in the HSV color space with a Gaussian blur, it creates visually striking backgrounds suitable for digital art, presentations, social media graphics, or any project needing a vibrant backdrop. Users can optionally add text and images with customizable positions.

## Features
- Iridescent Effect: Creates a shimmering background using 75 random lines with vibrant hues, blended with a 20-pixel Gaussian blur.
- Customizable Parameters: Adjust line count, opacity, blur, base color, and enhance vibrancy.
- Flexible Output: Generates backgrounds of any size with 600 DPI support.
- Optional Text Overlay: Add centered top text or custom-positioned text.
- Optional Image Overlay: Add user-provided images with customizable size and position.
- Lightweight: Built with Pillow and NumPy.
- Applications: Ideal for digital art, social media, presentations, websites, and more.

## Requirements
- Python Libraries: Pillow, NumPy.
- Python Version: 3.6 or higher.

## Installation
1. Ensure Python 3.6+ is installed.
2. Install via pip: pip install iridescent-bg
3. Verify: python -c "import iridescent_bg; print(iridescent_bg.__version__)"

## Usage
### Basic Background
Generate a black-based iridescent background:
   python
   from iridescent_bg import generate_iridescent_background
   from PIL import Image
   bg = generate_iridescent_background(width=1080, height=1080, enhance_vibrancy=True)
   bg.save("my_background.png", dpi=(600, 600))

### Add Centered Top Text
   python
   from iridescent_bg import generate_iridescent_background, add_text
   from PIL import Image
   bg = generate_iridescent_background(width=1080, height=1080, enhance_vibrancy=True)
   bg = add_text(bg, text="My Title", font_size=48, center_top=True)
   bg.save("my_text_background.png", dpi=(600, 600))

### Add Custom Image
   python
   from iridescent_bg import generate_iridescent_background, add_text, add_image
   from PIL import Image
   bg = generate_iridescent_background(width=1080, height=1080, enhance_vibrancy=True)
   bg = add_text(bg, text="My Project", font_size=48, center_top=True)
   bg = add_image(bg, side_image_path="path/to/your/image.jpg", width=540, position=(0, 0))
   bg.save("my_image_background.png", dpi=(600, 600))

## Configuration
- Default Settings: 1080×1080, black base, 75 lines, 100 opacity, 20 blur, 200 dash length.
- Customization: Adjust width, height, base_color (e.g., "#FF0000"), enhance_vibrancy, text position, image size/position.

## Example Outputs
See generated examples in the [repository](https://github.com/adams-charleen/iridescent-bg).

## Testing
Run unit tests: python -m unittest discover tests

## Notes
- The iridescent effect uses HSV for vibrant hues, varying each run.
- Ensure dependencies are installed.
- Customize base_color, text, and images as needed.

## License
MIT License. Free to use, modify, and distribute.

## Author
Developed by Charleen Adams. Contributions welcome at https://github.com/adams-charleen/iridescent-bg.
