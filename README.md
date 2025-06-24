# 🧠 Logo Similarity Challenge

This project explores various methods to **scrape logos from the web**, extract features, and **cluster similar brand logos** using computer vision techniques.

---

## 🌐 Web Scraping Performance

Attempted to extract logos from **4,384 domains** using a combination of APIs and scraping strategies. The best accuracy achieved was:

- ✅ **98.19% success** rate using a hybrid of multiple techniques

### 📈 Strategy Comparison:

| Method                                                                | % of Total              |
|-----------------------------------------------------------------------|-------------------------|
| Clearbit API                                                          | 84%                     |
| Clearbit API + Logo SVG Scraping (`*logo*.svg`)                       | 89%                     |
| Clearbit API + "Largest Logo" (heuristic on image size + filename)    | 100% ( but a lot of noise) |
| Clearbit API + Logo SVG Scraping +  Favicon Scraping + "Largest Logo" | 98.19%✅                 | 

### Best Method Breakdown
| Method                                                  | Count | Coverage |
|---------------------------------------------------------|-------|----------|
| Clearbit API                                            | 2912  | 86.77%   |
| Logo SVG Scraping                                       | 203   | 6.05%    |
| Favicon Scraping                                        | 241   | 7.18 %   |
| "Largest Logo"                                          | 0     | 0%       |

>  Attempting to extract logos via URL query parameters yielded **no improvement**.
### The output logos can be found in [this kaggle dataset](https://www.kaggle.com/datasets/mihaildanutdogaru/logo-similarity-data) containing:
- `extraction_method.csv` file with the logo extraction method
- `extracted_logos` dir containing the raw logos
- `resized_logos` dir with all logos resized to *128x128* pixels
- `logos.snappy.parquet` file containing the original domain names

---

## 🤖 Clustering Approaches

Explored different combinations of image preprocessing and feature extraction techniques to group similar logos using **DBSCAN** and **ResNet** embeddings.

---
> RGBA: Transparent RGB images  
> LA: Transparent Grayscale Images
### 📌 DBSCAN Clustering

#### Without Preprocessing:
- **RGBA**: 1,939 / 3,356 clustered  
- **LA**: 1,911 / 3,356 clustered

#### With Center Cropping (128x128 to 40x40):
- **LA**: Improved separation, 1,794 clustered  
  - ✅ Much better for cases like **AAMCO** with many variations  
- **RGBA**: 1,935 clustered

#### Blur + Crop:
- Around **2,300 logos marked as noise**, only ~1,000 successfully grouped  
- Performance was worse, potentially **overfitting**, only recognizing perfectly identical logos

#### Blur + Crop + Gaussian Noise:
- **RGBA**: 217 groups found, but **~75% marked as noise**  
- **LA**: Completely failed — **0 groups formed**, everything considered noise

#### Zernike Polynomials:
- ❌ Performance was **very poor**, not usable for this task

---

### 🧬 ResNet Feature Clustering

Using pre-trained ResNet50 embeddings for image similarity:

| Method                  | Clustered Logos / Total |
|-------------------------|--------------------------|
| ResNet (plain)          | 1,634 / 3,356✅            |
| ResNet + Gaussian Noise | 3,272 / 3,356            |
| ResNet + Jitter         | 2,624 / 3,356            |

--- 
### Final results 
- Can be found in `labeled_data.zip`
- The prefix number represents the corresponding group
- Prefix `-1` means the logo is not contained in any class

---


