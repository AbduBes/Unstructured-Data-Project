from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import os
import logging

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def convert_to_webp(path, output_path, quality=85):
    img = Image.open(path).convert('RGB')  
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'WEBP', quality=quality, optimize=True)
    orig_size = Path(path).stat().st_size
    new_size  = Path(output_path).stat().st_size
    saving_pct = round((1 - new_size / orig_size) * 100, 1)
    logger.info(f'WebP: {orig_size//1024}KB -> {new_size//1024}KB ({saving_pct}% saving)')
    return output_path


def inspect_image(image_path):
    
    try:
        img = Image.open(image_path)
        
        # Get file size
        file_size_bytes = os.path.getsize(image_path)
        file_size_kb = file_size_bytes / 1024
        file_size_mb = file_size_kb / 1024
        
        properties = {
            "filename": os.path.basename(image_path),
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": round(img.width / img.height, 3),
            "file_size_bytes": file_size_bytes,
            "file_size_kb": round(file_size_kb, 2),
            "file_size_mb": round(file_size_mb, 2),
        }
        
        logging.info(f"Inspected image: {properties['filename']}")
        return properties
        
    except Exception as e:
        logging.error(f"Error inspecting image {image_path}: {e}")
        return None


def resize_image(image_path, width, height, output_dir="data/processed/resized"):
   
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_resized.jpg")
        
        resized.save(output_path, "JPEG", quality=95)
        logging.info(f"Resized {image_path} to {width}x{height} -> {output_path}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error resizing image {image_path}: {e}")
        return None


def resize_proportional(image_path,output_dir="data/processed/resized", max_width=500):
   
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        
        # Calculate proportional height
        aspect_ratio = img.height / img.width
        target_height = int(max_width * aspect_ratio)
        
        resized = img.resize((max_width, target_height), Image.Resampling.LANCZOS)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_proportional.jpg")
        
        resized.save(output_path, "JPEG", quality=95)
        logging.info(f"Proportionally resized {image_path} to {max_width}x{target_height}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error in proportional resize {image_path}: {e}")
        return None


def generate_thumbnail(image_path, output_dir="data/processed/thumbnails", max_size=(200, 200)):
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        img_copy = img.copy()  # thumbnail() modifies in place
        
        img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_thumb.jpg")
        
        img_copy.save(output_path, "JPEG", quality=85)
        logging.info(f"Generated thumbnail for {image_path} -> {output_path}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error generating thumbnail {image_path}: {e}")
        return None


def generate_fixed_thumbnail(image_path, size=(300, 300), method="cover", 
                             output_dir="data/processed/thumbnails"):
  
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        
        # Choose method
        if method == "contain":
            thumb = ImageOps.contain(img, size, Image.Resampling.LANCZOS)
        elif method == "cover":
            thumb = ImageOps.cover(img, size, Image.Resampling.LANCZOS)
        elif method == "fit":
            thumb = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
        elif method == "pad":
            thumb = ImageOps.pad(img, size, Image.Resampling.LANCZOS, color="white")
        else:
            raise ValueError(f"Unknown method: {method}")
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_{method}_thumb.jpg")
        
        thumb.save(output_path, "JPEG", quality=85)
        logging.info(f"Generated {method} thumbnail for {image_path}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error generating fixed thumbnail {image_path}: {e}")
        return None


def crop_image(image_path, box, output_dir="data/processed/cropped"):
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        cropped = img.crop(box)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_cropped.jpg")
        
        cropped.save(output_path, "JPEG", quality=95)
        logging.info(f"Cropped {image_path} to box {box}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error cropping image {image_path}: {e}")
        return None


def crop_banner(image_path, output_dir="data/processed/cropped"):
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Crop top half
        box = (0, 0, width, height // 2)
        return crop_image(image_path, box, output_dir)
        
    except Exception as e:
        logging.error(f"Error creating banner from {image_path}: {e}")
        return None


def crop_center_square(image_path, output_dir="data/processed/cropped"):
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Determine square size (smaller dimension)
        size = min(width, height)
        
        # Calculate center box
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        box = (left, top, right, bottom)
        return crop_image(image_path, box, output_dir)
        
    except Exception as e:
        logging.error(f"Error creating center square from {image_path}: {e}")
        return None


def convert_format(image_path, target_format="WEBP", quality=85, 
                   output_dir="data/processed/webp"):
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (WebP doesn't support P mode)
        if img.mode in ("P", "RGBA") and target_format == "JPEG":
            img = img.convert("RGB")
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        extension = target_format.lower()
        if extension == "jpeg":
            extension = "jpg"
        
        output_path = os.path.join(output_dir, f"{base_name}.{extension}")
        
        if target_format == "WEBP":
            img.save(output_path, "WEBP", quality=quality)
        elif target_format == "PNG":
            img.save(output_path, "PNG", optimize=True)
        elif target_format == "JPEG":
            img.save(output_path, "JPEG", quality=quality)
        else:
            raise ValueError(f"Unsupported format: {target_format}")
        
        logging.info(f"Converted {image_path} to {target_format} -> {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Error converting {image_path} to {target_format}: {e}")
        return None


def apply_blur(image_path, radius=2, output_dir="data/processed/filtered"):
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_blur.jpg")
        
        blurred.save(output_path, "JPEG", quality=90)
        logging.info(f"Applied blur filter to {image_path}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error applying blur to {image_path}: {e}")
        return None


def apply_sharpen(image_path, output_dir="data/processed/filtered"):
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        sharpened = img.filter(ImageFilter.SHARPEN)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_sharp.jpg")
        
        sharpened.save(output_path, "JPEG", quality=90)
        logging.info(f"Applied sharpen filter to {image_path}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error applying sharpen to {image_path}: {e}")
        return None


def adjust_brightness(image_path, factor=1.5, output_dir="data/processed/filtered"):
   
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        brightened = enhancer.enhance(factor)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_bright.jpg")
        
        brightened.save(output_path, "JPEG", quality=90)
        logging.info(f"Adjusted brightness of {image_path} by factor {factor}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error adjusting brightness of {image_path}: {e}")
        return None


def adjust_contrast(image_path, factor=1.5, output_dir="data/processed/filtered"):
    """
    Adjust image contrast
    
    Args:
        image_path: Path to input image
        factor: Contrast factor (1.0 = original, >1 more contrast, <1 less)
        output_dir: Directory to save adjusted image
    
    Returns:
        Path to adjusted image
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        contrasted = enhancer.enhance(factor)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_contrast.jpg")
        
        contrasted.save(output_path, "JPEG", quality=90)
        logging.info(f"Adjusted contrast of {image_path} by factor {factor}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error adjusting contrast of {image_path}: {e}")
        return None


if __name__ == "__main__":
    # Test functions
    print("Image processor module loaded successfully")