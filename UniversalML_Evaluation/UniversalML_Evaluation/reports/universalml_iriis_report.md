# UniversalML Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: universalml/Nepali_Tokenizer
- Seed: 13
- Target words: 100,000
- Actual words: 100,000
- Documents used: 396
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100000 | 206440 | 2.0644 | 1 | 11 | 2.0644 | 2.0 | 3.0 |
| suffix_words | 28848 | 77004 | 2.6693 | 1 | 11 | 2.6693 | 2.0 | 4.0 |
| halanta_words | 35707 | 79991 | 2.2402 | 1 | 11 | 2.2402 | 2.0 | 4.0 |
| super_suffix_words | 711 | 2254 | 3.1702 | 2 | 8 | 3.1702 | 3.0 | 4.0 |
| chain_len_3plus | 15 | 50 | 3.3333 | 1 | 6 | 3.3333 | 3.0 | 4.0 |

## T/W Ratio (Document Level)
- Mean: 2.072
- Median: 2.0685736677115987
- P90: 2.258426966292135
- Min: 1.552
- Max: 2.652173913043478

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 3251 | 4632 | 1.4248 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 32 | 96 | 3.0 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 43764
- Tokens ending with halanta: 6590
- Integrity (1 - cliffhangers/total): 0.8494

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 28848
- Words with fragmented suffix: 653
- Fragmentation rate: 0.0226

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
