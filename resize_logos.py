# -------------------------------
# 🖼️ LOGO IMAGE RESIZER (Multithreaded)
# -------------------------------
# Resizes assets from `input_dir` and saves them to `output_dir`
# using Python's PIL and ThreadPoolExecutor for speed.
# -------------------------------

from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
import os

# -------------------------------
# 📁 Directory Setup
# -------------------------------

input_dir = 'extracted_logos'  # Folder containing original logos
output_dir = 'resized_logos'  # Folder to store resized assets
os.makedirs(output_dir, exist_ok=True)


# -------------------------------
# 🔧 Image Resizing Function
# -------------------------------

def resize_single_image(filename, input_dir, output_dir, size=(128, 128)):
    """
    Resize a single image and save to output_dir.

    Args:
        filename (str): Name of the image file.
        input_dir (str): Directory containing original assets.
        output_dir (str): Directory to save resized assets.
        size (tuple): Target size (width, height).
    """
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    try:
        img = Image.open(input_path).convert('RGB')
        img_resized = img.resize(size)
        img_resized.save(output_path)
    except Exception as e:
        print(f'❌ Error processing {filename}: {e}')


# -------------------------------
# ⚙️ Multithreaded Resizing
# -------------------------------

def resize_logos_multithreaded(input_dir, output_dir, size=(128, 128), max_threads=10):
    """
    Resize all assets in the input_dir using multithreading.

    Args:
        input_dir (str): Directory with original assets.
        output_dir (str): Output directory for resized assets.
        size (tuple): Resize target (width, height).
        max_threads (int): Number of threads to use.
    """
    # Get all image files with valid extensions
    valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_exts)]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Use tqdm for progress tracking
        list(tqdm(
            executor.map(
                lambda f: resize_single_image(f, input_dir, output_dir, size),
                image_files
            ),
            total=len(image_files),
            desc="🔄 Resizing assets"
        ))


# -------------------------------
# 🚀 Run Resizer
# -------------------------------

resize_logos_multithreaded(input_dir, output_dir)
