import logging
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os

# Bot settings
logging.basicConfig(level=logging.INFO)

def grayscale_image(image):
    """
    Converts the image to grayscale.
    """
    return image.convert("L")

def ascii_char_from_pixel(pixel_value, gradient):
    """
    Maps a pixel value (0 to 255) to a character from the provided gradient.
    """
    index = int(pixel_value / 255 * (len(gradient) - 1))
    return gradient[index]

def image_to_ascii(image_path, new_width, aspect_ratio_adjust, upscale_factor, invert, gradient):
    """
    Converts an image to ASCII art using a specified gradient of characters.
    Includes relative normalization for improving contrast in uniformly lit images.
    """
    image = Image.open(image_path)
    
    # Auto-adjust the contrast of the image
    image = ImageOps.autocontrast(image)
    
    # Enhance details in the image
    image = image.filter(ImageFilter.DETAIL)
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    
    # Upscale the image to improve fine details
    original_width, original_height = image.size
    image = image.resize((original_width * upscale_factor, original_height * upscale_factor), Image.BICUBIC)
    
    # Calculate the new height based on the aspect ratio and new width
    width, height = image.size
    ratio = height / width
    new_height = max(1, int(new_width * ratio * aspect_ratio_adjust))
    image = image.resize((new_width, new_height), Image.BICUBIC)
    
    # Convert the image to grayscale
    image = grayscale_image(image)
    
    # Get the pixel array and apply normalization based on the min and max values
    pixels = np.array(image).astype(np.float32)
    min_val = pixels.min()
    max_val = pixels.max()
    
    if max_val - min_val > 0:
        normalized_pixels = (pixels - min_val) / (max_val - min_val) * 255
    else:
        normalized_pixels = pixels  # If the image is uniform
    
    # Invert the gradient if needed
    if invert:
        gradient = gradient[::-1]
    
    # Convert each pixel to the corresponding ASCII character
    ascii_str = "".join(ascii_char_from_pixel(int(pixel), gradient) for pixel in normalized_pixels.flatten())
    
    # Split the ASCII characters into lines based on the new width
    ascii_img = "\n".join(ascii_str[i:i+new_width] for i in range(0, len(ascii_str), new_width))
    
    return ascii_img
