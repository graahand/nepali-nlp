# Qwen Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: Qwen/Qwen3-8B
- Seed: 13
- Target words: 4,000,000
- Actual words: 4,000,000
- Documents used: 17,057
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 4000000 | 23138610 | 5.7847 | 1 | 60 | 5.7847 | 5.0 | 9.0 |
| suffix_words | 1155515 | 8817531 | 7.6308 | 3 | 50 | 7.6308 | 7.0 | 11.0 |
| halanta_words | 1428486 | 10640700 | 7.4489 | 1 | 60 | 7.4489 | 7.0 | 11.0 |
| super_suffix_words | 28558 | 265390 | 9.293 | 5 | 22 | 9.293 | 9.0 | 12.0 |
| chain_len_3plus | 803 | 8760 | 10.9091 | 8 | 24 | 10.9091 | 11.0 | 15.0 |

## T/W Ratio (Document Level)
- Mean: 5.827
- Median: 5.8283582089552235
- P90: 6.342541436464089
- Min: 3.4285714285714284
- Max: 9.0

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 136937 | 525706 | 3.839 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 20 | 400 | 20.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 2964 | 33149 | 11.1839 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 1767739
- Tokens ending with halanta: 0
- Integrity (1 - cliffhangers/total): 1.0

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 1155515
- Words with fragmented suffix: 0
- Fragmentation rate: 0.0

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
