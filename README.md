# logo_similarity_challenge

## Web Scraping

Could only only read 3416/4384 \(77.91\%\) domains

- clearbit API: 84%
- clearbit API + webscrap('\*logo\*.svg'): 89%
- clearbit API + webscrap('\*logo\*.svg') + favicon: %
- clearbit API + webscrap(largest '\*logo\*'): 100% but a lot of noise with bad images that are not logos

- clearbit, scrap svg, favicon, scrap largest: 98.19%
📊 Extraction Method Breakdown:
  - clearbit: 2912 (86.77%)
  - scrap_favicon: 241 (7.18%)
  - scrap_logo: 203 (6.05%)
  - scrap_largest: 0 (0%)

- tried using the logos that are a url query, 0 no improvements

## Clustering
### DBSCAN
- no transforms
  - RGBA: 1939/3356
  - LA: 1911/3356
- crop:
  - LA: good separation, noise: 1794/3356, a lot better for AAMCO
  - RGBA: noise 1935/3356
- blur + crop: not a big inorivement, around 2300 images as noise, 1000 grouped, mostly overfit
  - RGBA
  - LA: 203 groups and a lot of noise, bad
- blur + crop + noise:
  - RGBA: found 217groups but around 3/4 was consideres noise, bad
  - LA: ALL NOISE, 0 LEARN FFS 