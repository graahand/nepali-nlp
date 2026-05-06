# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: sentencepiece
- Seed: 13
- Target words: 100,000
- Actual words: 100,000
- Documents used: 396
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100000 | 332079 | 3.3208 | 3 | 12 | 3.3208 | 3.0 | 4.0 |
| suffix_words | 28848 | 104656 | 3.6278 | 3 | 12 | 3.6278 | 3.0 | 4.0 |
| halanta_words | 35707 | 121391 | 3.3996 | 3 | 12 | 3.3996 | 3.0 | 4.0 |
| super_suffix_words | 711 | 2576 | 3.6231 | 3 | 6 | 3.6231 | 4.0 | 4.0 |
| chain_len_3plus | 15 | 63 | 4.2 | 3 | 7 | 4.2 | 4.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 3.3066
- Median: 3.2915792711916545
- P90: 3.4550669216061185
- Min: 3.074626865671642
- Max: 4.0

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 3251 | 10132 | 3.1166 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 32 | 140 | 4.375 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 43764
- Tokens ending with halanta: 2349
- Integrity (1 - cliffhangers/total): 0.9463

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 28848
- Words with fragmented suffix: 0
- Fragmentation rate: 0.0

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
