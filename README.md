# logo_similarity_challenge

## Web Scraping

Could only only read 3416/4384 \(77.91\%\) domains

- clearbit API: 84%
- clearbit API + webscrap('\*logo\*.svg'): 89%
- clearbit API + webscrap('\*logo\*.svg') + favicon: %
- clearbit API + webscrap(largest '\*logo\*'): 100% but a lot of noise with bad images that are not logos

- clearbit, scrap svg, favicon, scrap largest: 98.19%
   📊 Extraction Method Breakdown:
  - clearbit: 2905 (86.56%)
  - scrap_favicon: 430 (12.81%)
  - scrap_largest: 21 (0.63%)
