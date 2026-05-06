# Qwen Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: Qwen/Qwen3-8B
- Seed: 13
- Target words: 100,000
- Actual words: 100,000
- Documents used: 396
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100000 | 577778 | 5.7778 | 1 | 28 | 5.7778 | 5.0 | 9.0 |
| suffix_words | 28848 | 220741 | 7.6519 | 3 | 28 | 7.6519 | 7.0 | 11.0 |
| halanta_words | 35707 | 263771 | 7.3871 | 3 | 28 | 7.3871 | 7.0 | 11.0 |
| super_suffix_words | 711 | 6706 | 9.4318 | 5 | 20 | 9.4318 | 9.0 | 12.0 |
| chain_len_3plus | 15 | 155 | 10.3333 | 8 | 15 | 10.3333 | 10.0 | 12.0 |

## T/W Ratio (Document Level)
- Mean: 5.808
- Median: 5.820761662539322
- P90: 6.304878048780488
- Min: 3.888888888888889
- Max: 7.362397820163488

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 3251 | 12564 | 3.8647 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 32 | 375 | 11.7188 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 43764
- Tokens ending with halanta: 0
- Integrity (1 - cliffhangers/total): 1.0

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 28848
- Words with fragmented suffix: 0
- Fragmentation rate: 0.0

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
