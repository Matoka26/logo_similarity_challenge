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

input_name = 'logos.snappy.parquet'
save_dir = 'extracted_logos'
extraction_method_csv = 'extraction_method'
os.makedirs(save_dir, exist_ok=True)

timeout = 10
headers_browser = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}


def webscrap_logo_largest(domain):
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
    url = f'https://{domain}'
    try:
        response = requests.get(url, timeout=timeout, headers=headers_browser)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if re.search(r'logo', src, re.IGNORECASE) or \
                        re.search(r'logo', (img.get('alt') or ''), re.IGNORECASE) or \
                        re.search(r'logo', (img.get('class') or [''])[0], re.IGNORECASE):
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
    url_google = f"https://www.google.com/s2/favicons?sz=64&domain_url={domain}"
    try:
        response = requests.get(url_google, timeout=timeout)
        if response.status_code == 200 and response.content:
            return response.content
    except Exception as e:
        pass

    return None

def webscrap_clearbit(domain):
    url = f'https://logo.clearbit.com/{domain}'
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200 and response.content:
            return response.content
    except Exception as e:
        pass

    return None


def fetch_logo(domain):
    filename = f'{save_dir}/{domain}.png'
    result = None
    method = None

    # 1. Try Clearbit
    if result is None:
        result = webscrap_clearbit(domain)
        method = 'clearbit' if result else None

    # 2. Try SVG logo
    if result is None:
        result = webscrap_logo(domain)
        method = 'scrap_logo' if result else None

    # 3. Try favicon
    if result is None:
        result = webscrap_favicon(domain)
        method = 'scrap_favicon' if result else None

    # 4. Try largest logo
    if result is None:
        result = webscrap_logo_largest(domain)
        method = 'scrap_largest' if result else None

    # Save if any method succeeded
    if result:
        with open(filename, 'wb') as f:
            f.write(result)

    return (domain, method)


def extract_logos_multithreaded(file, max_threads=10):
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

                if method is not None:
                    extracted += 1
                    method_counter[method] += 1
                else:
                    failed += 1
                    method = "failed"
                    print(f"\n❌ Failed to get logo for {domain}")

                domain_results.append((domain, method))

            except Exception as e:
                print(f"❌ Exception for {domain}: {e}")
                failed += 1
                domain_results.append((domain, "failed"))

    total = len(domains)
    print(f"\n✅ Extracted: {extracted}/{total} ({(extracted / total):.2%})")
    print(f"❌ Failed to access: {failed}")

    # Save domain results to CSV
    method_df = pd.DataFrame(domain_results, columns=["domain", "method"])
    method_df.to_csv(extraction_method_csv + '.csv', index=False)
    print(f"📄 Saved domain extraction results to {extraction_method_csv}")

    # Print breakdown
    print("\n📊 Extraction Method Breakdown:")
    for method, count in method_counter.items():
        pct = 100 * count / extracted if extracted > 0 else 0
        print(f"  - {method}: {count} ({pct:.2f}%)")


extract_logos_multithreaded(input_name, max_threads=16)

