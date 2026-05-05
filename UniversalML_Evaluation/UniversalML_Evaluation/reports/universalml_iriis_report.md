# UniversalML Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: universalml/Nepali_Tokenizer
- Seed: 13
- Target words: 4,000,000
- Actual words: 4,000,000
- Documents used: 17,057
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 4000000 | 8258454 | 2.0646 | 1 | 31 | 2.0646 | 2.0 | 3.0 |
| suffix_words | 1155515 | 3072496 | 2.659 | 1 | 31 | 2.659 | 2.0 | 4.0 |
| halanta_words | 1428486 | 3207867 | 2.2456 | 1 | 31 | 2.2456 | 2.0 | 4.0 |
| super_suffix_words | 28558 | 87248 | 3.0551 | 2 | 8 | 3.0551 | 3.0 | 4.0 |
| chain_len_3plus | 803 | 2504 | 3.1183 | 1 | 10 | 3.1183 | 3.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 2.0704
- Median: 2.0688836104513064
- P90: 2.240816326530612
- Min: 1.3
- Max: 3.272727272727273

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 136937 | 195559 | 1.4281 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 20 | 117 | 5.85 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 2964 | 9263 | 3.1252 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 1767739
- Tokens ending with halanta: 248518
- Integrity (1 - cliffhangers/total): 0.8594

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 1155515
- Words with fragmented suffix: 21822
- Fragmentation rate: 0.0189

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
