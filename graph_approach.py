import os
import cv2
import networkx as nx
from itertools import combinations
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# Parameters
IMAGE_DIR = "data/resized_logos/"
SSIM_THRESHOLD = 0.40

# Load all assets
def load_images(directory):
    images = {}
    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images[fname] = img
    return images

# Worker function to compute SSIM
def compare_pair(args):
    (name1, img1), (name2, img2), threshold = args
    score, _ = ssim(img1, img2, full=True)
    if score >= threshold:
        return (name1, name2)
    return None

# Build similarity graph using multiprocessing
def build_graph(images, threshold):
    G = nx.Graph()
    G.add_nodes_from(images.keys())

    pairs = list(combinations(images.items(), 2))
    args = [((name1, img1), (name2, img2), threshold) for (name1, img1), (name2, img2) in pairs]

    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm(pool.imap_unordered(compare_pair, args), total=len(args)))

    for result in results:
        if result:
            G.add_edge(*result)

    return G


if __name__ == "__main__":
    images = load_images(IMAGE_DIR)
    graph = build_graph(images, SSIM_THRESHOLD)
    clusters = list(nx.connected_components(graph))

    # Output results
    print(f"\nTotal clusters found: {len(clusters)}")
    for i, cluster in enumerate(clusters, 1):
        print(f"Cluster {i}: {sorted(cluster)}")
