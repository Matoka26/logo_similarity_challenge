# -------------------------------
# 🧠 LOGO EXTRACTION PIPELINE
# -------------------------------
# Extract logos from a list of domains using multiple techniques:
# 1. Clearbit API
# 2. Web scraping (<img> tags with 'logo' in src/alt/class)
# 3. Favicon fallback
# 4. Largest 'logo-like' image
#
# Results saved to PNG files in 'extracted_logos/' and method breakdown in a CSV.
# -------------------------------

from tqdm import tqdm
from urllib.parse import urljoin
from collections import Counter
import pandas as pd
import numpy as np
import cv2
import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# -------------------------------
# 📁 Input / Output Configuration
# -------------------------------

input_name = 'logos.snappy.parquet'           # Input file with 'domain' column
save_dir = 'extracted_logos'                  # Directory to save logos
extraction_method_csv = 'extraction_method'   # CSV to log which method was used
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# 🌍 HTTP Configuration
# -------------------------------

timeout = 10  # seconds
headers_browser = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}

# -------------------------------
# 🔍 Scraping Utilities
# -------------------------------

def webscrap_logo_largest(domain):
    """
    Attempt to download the largest logo-like image based on <img> tags
    with 'logo' in the src attribute.
    """
    url = f'https://{domain}'
    try:
        response = requests.get(url, timeout=timeout, headers=headers_browser)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            candidate_imgs = []

            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if src and re.search(r'logo', src, re.IGNORECASE):
                    full_url = urljoin(url, src)
                    candidate_imgs.append(full_url)

            # Choose the largest image by area
            largest_img = None
            largest_area = 0

            for im_url in candidate_imgs:
                try:
                    img_resp = requests.get(im_url, timeout=timeout, headers=headers_browser)
                    if img_resp.status_code == 200:
                        image_bytes = np.asarray(bytearray(img_resp.content), dtype=np.uint8)
                        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                        if img is not None:
                            h, w = img.shape[:2]
                            area = h * w
                            if area > largest_area:
                                largest_img = img
                                largest_area = area
                except Exception:
                    continue

            if largest_img is not None:
                success, buffer = cv2.imencode('.png', largest_img)
                if success:
                    return buffer.tobytes()
    except Exception:
        pass

    return None


def webscrap_logo(domain):
    """
    Scrape <img> tags with 'logo' in src, alt, or class.
    """
    url = f'https://{domain}'
    try:
        response = requests.get(url, timeout=timeout, headers=headers_browser)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if re.search(r'logo', src or '', re.IGNORECASE) or \
                   re.search(r'logo', (img.get('alt') or ''), re.IGNORECASE) or \
                   re.search(r'logo', ' '.join(img.get('class') or []), re.IGNORECASE):
                    full_url = urljoin(url, src)
                    img_resp = requests.get(full_url, timeout=timeout, headers=headers_browser)
                    if img_resp.status_code == 200:
                        image_bytes = np.asarray(bytearray(img_resp.content), dtype=np.uint8)
                        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                        if img is not None:
                            success, buffer = cv2.imencode('.png', img)
                            if success:
                                return buffer.tobytes()
    except Exception:
        pass
    return None


def webscrap_favicon(domain):
    """
    Fetch favicon using Google’s public favicon service.
    """
    url_google = f"https://www.google.com/s2/favicons?sz=64&domain_url={domain}"
    try:
        response = requests.get(url_google, timeout=timeout)
        if response.status_code == 200 and response.content:
            return response.content
    except Exception:
        pass
    return None


def webscrap_clearbit(domain):
    """
    Try getting logo via Clearbit API.
    """
    url = f'https://logo.clearbit.com/{domain}'
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200 and response.content:
            return response.content
    except Exception:
        pass
    return None

# -------------------------------
# 📦 Main Logo Fetcher
# -------------------------------

def fetch_logo(domain):
    """
    Try all methods in order and save the first successful image.
    """
    filename = f'{save_dir}/{domain}.png'
    result = None
    method = None

    for method_name, func in [
        ('clearbit', webscrap_clearbit),
        ('scrap_logo', webscrap_logo),
        ('scrap_favicon', webscrap_favicon),
        ('scrap_largest', webscrap_logo_largest)
    ]:
        result = func(domain)
        if result:
            method = method_name
            break

    if result:
        with open(filename, 'wb') as f:
            f.write(result)

    return (domain, method)


# -------------------------------
# ⚙️ Multi-threaded Processing
# -------------------------------

def extract_logos_multithreaded(file, max_threads=10):
    """
    Process all domains using threads and log which method worked.
    """
    df = pd.read_parquet(file)
    domains = df['domain'].dropna().unique().tolist()

    extracted, failed = 0, 0
    method_counter = Counter()
    domain_results = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(fetch_logo, domain): domain for domain in domains}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading logos"):
            domain = futures[future]
            try:
                result = future.result()
                method = result[1]

                if method:
                    extracted += 1
                    method_counter[method] += 1
                else:
                    failed += 1
                    print(f"\n❌ Failed to get logo for {domain}")
                    method = "failed"

                domain_results.append((domain, method))

            except Exception as e:
                print(f"❌ Exception for {domain}: {e}")
                failed += 1
                domain_results.append((domain, "failed"))

    total = len(domains)
    print(f"\n✅ Extracted: {extracted}/{total} ({(extracted / total):.2%})")
    print(f"❌ Failed: {failed}")

    # Save CSV with results
    method_df = pd.DataFrame(domain_results, columns=["domain", "method"])
    method_df.to_csv(extraction_method_csv + '.csv', index=False)
    print(f"📄 Saved extraction methods to {extraction_method_csv}.csv")

    # Show stats
    print("\n📊 Extraction Method Breakdown:")
    for method, count in method_counter.items():
        pct = 100 * count / extracted if extracted else 0
        print(f"  - {method}: {count} ({pct:.2f}%)")


# -------------------------------
# 🚀 Run
# -------------------------------

extract_logos_multithreaded(input_name, max_threads=16)
