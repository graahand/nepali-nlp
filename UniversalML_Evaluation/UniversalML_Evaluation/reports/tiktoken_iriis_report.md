# TikToken Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Encoding: o200k_base
- Seed: 13
- Target words: 4,000,000
- Actual words: 4,000,000
- Documents used: 17,057
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 4000000 | 11378886 | 2.8447 | 1 | 40 | 2.8447 | 3.0 | 4.0 |
| suffix_words | 1155515 | 4095854 | 3.5446 | 1 | 33 | 3.5446 | 3.0 | 5.0 |
| halanta_words | 1428486 | 4816245 | 3.3716 | 1 | 40 | 3.3716 | 3.0 | 5.0 |
| super_suffix_words | 28558 | 104715 | 3.6667 | 1 | 12 | 3.6667 | 3.0 | 5.0 |
| chain_len_3plus | 803 | 3736 | 4.6526 | 3 | 13 | 4.6526 | 5.0 | 6.0 |

## T/W Ratio (Document Level)
- Mean: 2.8511
- Median: 2.8536585365853657
- P90: 3.0707070707070705
- Min: 1.0
- Max: 4.363636363636363

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 136937 | 206830 | 1.5104 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 20 | 179 | 8.95 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 2964 | 10792 | 3.641 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 1767739
- Tokens ending with halanta: 70266
- Integrity (1 - cliffhangers/total): 0.9603

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 1155515
- Words with fragmented suffix: 15903
- Fragmentation rate: 0.0138

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
