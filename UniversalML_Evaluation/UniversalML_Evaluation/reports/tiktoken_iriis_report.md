# TikToken Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Encoding: o200k_base
- Seed: 13
- Target words: 100,000
- Actual words: 100,000
- Documents used: 396
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100000 | 284858 | 2.8486 | 1 | 14 | 2.8486 | 3.0 | 4.0 |
| suffix_words | 28848 | 102524 | 3.5539 | 1 | 14 | 3.5539 | 3.0 | 5.0 |
| halanta_words | 35707 | 120028 | 3.3615 | 1 | 14 | 3.3615 | 3.0 | 5.0 |
| super_suffix_words | 711 | 2658 | 3.7384 | 1 | 10 | 3.7384 | 4.0 | 5.0 |
| chain_len_3plus | 15 | 64 | 4.2667 | 3 | 6 | 4.2667 | 4.0 | 6.0 |

## T/W Ratio (Document Level)
- Mean: 2.8488
- Median: 2.8490249461820945
- P90: 3.074074074074074
- Min: 2.2222222222222223
- Max: 3.6363636363636362

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 3251 | 4926 | 1.5152 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 32 | 114 | 3.5625 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 43764
- Tokens ending with halanta: 2065
- Integrity (1 - cliffhangers/total): 0.9528

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 28848
- Words with fragmented suffix: 494
- Fragmentation rate: 0.0171

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
