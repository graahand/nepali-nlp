# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: wordpiece
- Seed: 13
- Target words: 4,000,000
- Actual words: 4,000,000
- Documents used: 17,057
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 4000000 | 13043192 | 3.2608 | 2 | 34 | 3.2608 | 3.0 | 4.0 |
| suffix_words | 1155515 | 3956809 | 3.4243 | 3 | 34 | 3.4243 | 3.0 | 4.0 |
| halanta_words | 1428486 | 4802661 | 3.3621 | 3 | 34 | 3.3621 | 3.0 | 4.0 |
| super_suffix_words | 28558 | 98905 | 3.4633 | 3 | 9 | 3.4633 | 3.0 | 4.0 |
| chain_len_3plus | 803 | 3069 | 3.8219 | 3 | 10 | 3.8219 | 4.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 3.2584
- Median: 3.2421052631578946
- P90: 3.404040404040404
- Min: 3.0
- Max: 4.515151515151516

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 136937 | 426893 | 3.1174 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 20 | 210 | 10.5 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 2964 | 12811 | 4.3222 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 1767739
- Tokens ending with halanta: 105960
- Integrity (1 - cliffhangers/total): 0.9401

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 1155515
- Words with fragmented suffix: 68
- Fragmentation rate: 0.0001

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
