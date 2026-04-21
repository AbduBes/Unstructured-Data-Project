#!/usr/bin/env python3
"""
Test script for all image processing functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'image_processing'))

from processor import *


def test_single_image(image_path):
    """Test all processing functions on a single image"""
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    print("=" * 60)
    print(f"Testing Image Processing Functions")
    print(f"Image: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Test 1: Inspect Image
    print("\n1. Inspecting Image Properties...")
    props = inspect_image(image_path)
    if props:
        print(f"   ✓ Format: {props['format']}")
        print(f"   ✓ Size: {props['width']}x{props['height']}")
        print(f"   ✓ Aspect Ratio: {props['aspect_ratio']}")
        print(f"   ✓ File Size: {props['file_size_kb']} KB")
    
    # Test 2: Resize
    print("\n2. Testing Resize Functions...")
    resized = resize_proportional(image_path, max_width=400)
    if resized:
        print(f"   ✓ Proportional resize: {resized}")
    
    exact_resized = resize_image(image_path, width=300, height=400)
    if exact_resized:
        print(f"   ✓ Exact resize: {exact_resized}")
    
    # Test 3: Thumbnails
    print("\n3. Testing Thumbnail Generation...")
    thumb = generate_thumbnail(image_path, max_size=(150, 150))
    if thumb:
        print(f"   ✓ Basic thumbnail: {thumb}")
    
    fixed_thumb = generate_fixed_thumbnail(image_path, size=(200, 200), method="cover")
    if fixed_thumb:
        print(f"   ✓ Fixed cover thumbnail: {fixed_thumb}")
    
    # Test 4: Cropping
    print("\n4. Testing Crop Functions...")
    banner = crop_banner(image_path)
    if banner:
        print(f"   ✓ Banner crop: {banner}")
    
    square = crop_center_square(image_path)
    if square:
        print(f"   ✓ Center square crop: {square}")
    
    # Test 5: Format Conversion
    print("\n5. Testing Format Conversion...")
    webp = convert_format(image_path, target_format="WEBP", quality=85)
    if webp:
        print(f"   ✓ WebP conversion: {webp}")
    
    png = convert_format(image_path, target_format="PNG")
    if png:
        print(f"   ✓ PNG conversion: {png}")
    
    # Test 6: Filters and Enhancements
    print("\n6. Testing Filters and Enhancements...")
    blurred = apply_blur(image_path, radius=3)
    if blurred:
        print(f"   ✓ Blur filter: {blurred}")
    
    sharp = apply_sharpen(image_path)
    if sharp:
        print(f"   ✓ Sharpen filter: {sharp}")
    
    bright = adjust_brightness(image_path, factor=1.3)
    if bright:
        print(f"   ✓ Brightness adjustment: {bright}")
    
    contrast = adjust_contrast(image_path, factor=1.4)
    if contrast:
        print(f"   ✓ Contrast adjustment: {contrast}")
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)


def main():
    # Find first image in data/raw/images
    image_dir = "data/raw/images"
    
    if not os.path.exists(image_dir):
        print(f"Error: Directory not found: {image_dir}")
        print("Please run test_download.py first to download some images")
        return
    
    image_files = [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    
    if not image_files:
        print(f"Error: No images found in {image_dir}")
        print("Please run test_download.py first to download some images")
        return
    
    # Test with first image
    test_single_image(image_files[1])


if __name__ == "__main__":
    main()