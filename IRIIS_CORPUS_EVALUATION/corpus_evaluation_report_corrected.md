# Nepali Corpus Evaluation Report
*LINGUA-NEP / IRIIS-RESEARCH/Nepali-Text-Corpus*

## 1. Corpus Size Metrics
- **Total Documents (post-dedup):** 5,176,975
- **Exact Duplicates Removed:** 23,025  (0.44%)
- **Total Sentences:** 84,890,912
- **Total Words (tokens):** 1,221,814,455
- **Total Characters:** 8,344,616,414
- **Total Bytes (UTF-8):** 22,373,887,781 (≈ 20.84 GB)

## 2. Vocabulary & Typology
- **Unique Word Types:** 5,517,510
- **Type-Token Ratio (TTR):** 0.00452
- **Hapax Legomena:** 2,645,392
- **Hapax / Total Tokens:** 0.00217
- **Hapax / Unique Types:** 0.47945

## 3. Source / Domain Distribution
- **ratopati.com**: 308,638
- **gorkhapatraonline.com**: 279,640
- **ekantipur.com**: 215,317
- **nepalkhabar.com**: 195,445
- **annapurnapost.com**: 183,946
- **imagekhabar.com**: 181,443
- **reportersnepal.com**: 170,573
- **newsofnepal.com**: 156,199
- **lokpath.com**: 150,252
- **setopati.com**: 138,866
- **kendrabindu.com**: 137,212
- **makalukhabar.com**: 123,538
- **drishtinews.com**: 118,406
- **hamrakura.com**: 118,239
- **nepallive.com**: 115,953

## 4. Length Distributions
### Document Lengths (sentences)
- Mean: 16.4 | Median: 10 | Q1: 6 | Q3: 19 | Max: 2092
### Document Lengths (words)
- Mean: 236.01 | Median: 161 | Q1: 94 | Q3: 276 | Max: 24152
### Sentence Lengths (words)
- Mean: 14.39 | Median: 13 | Q1: 9 | Q3: 18 | Max: 2918

## 5. Devanagari vs Latin Script Ratio
- **Devanagari Characters:** 6,990,410,258
- **Latin Characters:** 0
- **Ratio:** 100.00% Devanagari / 0.00% Latin
- **Other (punct, space, symbols):** 1,354,206,156

## 6. Digit Distribution (Devanagari vs ASCII)
- **Devanagari Digits (०–९):** 81,612,017
- **ASCII Digits (0–9):** 0
- **Ratio:** 100.00% Devanagari / 0.00% ASCII

  > **LinguaBPE H3:** High Devanagari-digit ratio justifies numeral normalisation layer.

## 7. Halanta & Conjuncts
- **Halanta (् U+094D) Count:** 538,495,258
- **Halanta Density:** 7.7033% of all Devanagari chars
  > **LinguaBPE H2:** Each Halanta = one conjunct vulnerable to byte-level fragmentation.

## 8. Suffix-bearing Words
- **Suffix-bearing Words:** 337,156,050 (27.59% of total)
  > Longest-first matching: हरुको counted as हरुको, not को.
- **Per-suffix counts:**
  - `को`: 113,055,535  (33.53%)
  - `मा`: 68,330,516  (20.27%)
  - `ले`: 55,472,127  (16.45%)
  - `का`: 53,038,703  (15.73%)
  - `लाई`: 18,867,610  (5.60%)
  - `बाट`: 8,496,332  (2.52%)
  - `की`: 4,527,706  (1.34%)
  - `सँग`: 3,040,520  (0.90%)
  - `हरु`: 2,353,704  (0.70%)
  - `हरू`: 2,199,232  (0.65%)
  - `भन्दा`: 1,845,087  (0.55%)
  - `हरुले`: 1,380,654  (0.41%)
  - `सँगै`: 1,263,249  (0.37%)
  - `हरुको`: 1,163,379  (0.35%)
  - `हरुलाई`: 871,437  (0.26%)
  - `हरुमा`: 445,469  (0.13%)
  - `तिर`: 431,393  (0.13%)
  - `हरुका`: 158,849  (0.05%)
  - `हरुसँग`: 137,368  (0.04%)
  - `हरुबाट`: 76,777  (0.02%)

## 9. Noise Rates
- **HTML Remnants:** 18
- **URLs:** 0
- **Phone Numbers:** 12,988
- **Emojis:** 0

## 10. Top 50 Most Frequent Words
- `छ`: 23,476,790
- `र`: 21,675,422
- `पनि`: 10,790,404
- `भएको`: 9,073,826
- `छन्`: 8,677,935
- `गरेको`: 7,153,683
- `लागि`: 6,773,368
- `हो`: 6,171,993
- `तथा`: 5,796,179
- `भने`: 5,796,174
- `गर्न`: 5,475,477
- `गर्ने`: 5,450,547
- `थियो`: 5,251,727
- `उनले`: 4,497,549
- `रहेको`: 4,145,280
- `एक`: 3,817,349
- `हुने`: 3,639,622
- `यो`: 3,463,896
- `गरेका`: 3,402,255
- `नै`: 3,367,739
- `थिए`: 3,318,257
- `नेपाल`: 3,161,836
- `गरिएको`: 3,044,470
- `हजार`: 3,001,982
- `बताए`: 2,969,411
- `काठमाडौं`: 2,931,995
- `तर`: 2,823,925
- `गरी`: 2,681,149
- `गर्दै`: 2,521,140
- `काम`: 2,500,797
- `नेपाली`: 2,393,858
- `भएका`: 2,389,567
- `मा`: 2,309,678
- `दुई`: 2,145,687
- `जानकारी`: 2,096,800
- `सय`: 2,020,478
- `कारण`: 1,999,827
- `हुन्`: 1,984,009
- `अनुसार`: 1,952,554
- `भन्ने`: 1,949,029
- `लाख`: 1,942,772
- `अध्यक्ष`: 1,919,768
- `प्रहरी`: 1,909,914
- `१`: 1,899,291
- `केही`: 1,850,456
- `प्रमुख`: 1,792,328
- `को`: 1,763,728
- `५`: 1,746,316
- `’`: 1,723,987
- `दिन`: 1,722,235
