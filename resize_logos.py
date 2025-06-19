from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
import os

input_dir = 'extracted_logos'
output_dir = 'resized_logos'
os.makedirs(output_dir, exist_ok=True)


def resize_single_image(filename, input_dir, output_dir, size=(128, 128)):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    try:
        img = Image.open(input_path).convert('RGB')
        img_resized = img.resize(size)
        img_resized.save(output_path)
    except Exception as e:
        print(f'Error processing {filename}: {e}')


def resize_logos_multithreaded(input_dir, output_dir, size=(128, 128), max_threads=10):
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        list(tqdm(executor.map(
            lambda filename: resize_single_image(filename, input_dir, output_dir, size),
            image_files),
            total=len(image_files),
            desc="Resizing images"
        ))


resize_logos_multithreaded(input_dir, output_dir)
