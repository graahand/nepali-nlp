# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: wordpiece
- Seed: 13
- Target words: 100,000
- Actual words: 100,000
- Documents used: 396
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100000 | 328080 | 3.2808 | 3 | 13 | 3.2808 | 3.0 | 4.0 |
| suffix_words | 28848 | 99871 | 3.462 | 3 | 13 | 3.462 | 3.0 | 4.0 |
| halanta_words | 35707 | 121086 | 3.3911 | 3 | 13 | 3.3911 | 3.0 | 4.0 |
| super_suffix_words | 711 | 2502 | 3.519 | 3 | 9 | 3.519 | 3.0 | 4.0 |
| chain_len_3plus | 15 | 57 | 3.8 | 3 | 7 | 3.8 | 4.0 | 4.0 |

## T/W Ratio (Document Level)
- Mean: 3.2671
- Median: 3.243237407427826
- P90: 3.4163498098859315
- Min: 3.0
- Max: 3.796208530805687

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 3251 | 10141 | 3.1193 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 32 | 142 | 4.4375 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 43764
- Tokens ending with halanta: 3064
- Integrity (1 - cliffhangers/total): 0.93

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 28848
- Words with fragmented suffix: 2
- Fragmentation rate: 0.0001

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
