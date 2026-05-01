# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: wordpiece
- Seed: 13
- Target words: 40,000
- Actual words: 40,000
- Documents used: 168
- Partial last doc: False

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40000 | 130828 | 3.2707 | 3 | 13 | 3.2707 | 3.0 | 4.0 |
| suffix_words | 13002 | 44327 | 3.4092 | 3 | 13 | 3.4092 | 3.0 | 4.0 |
| halanta_words | 14370 | 48541 | 3.3779 | 3 | 13 | 3.3779 | 3.0 | 4.0 |
| super_suffix_words | 316 | 1102 | 3.4873 | 3 | 9 | 3.4873 | 3.0 | 4.0 |
| chain_len_3plus | 15 | 57 | 3.8 | 3 | 7 | 3.8 | 3.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 3.2632
- Median: 3.2432227663309616
- P90: 3.4017467248908297
- Min: 3.0597014925373136
- Max: 3.783333333333333

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 1338 | 4192 | 3.133 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 7 | 28 | 4.0 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity
- Total conjuncts: 15907
- Fragmented conjuncts: 648
- Integrity (1 - fragmented/total): 0.9593

## Morphological Loss (Postpositions)
- Words with suffix chain: 13002
- Words with severed suffix token: 2626
- Severance rate: 0.202

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity checks whether each conjunct appears intact in any token.
- Document ratios are computed only for full documents in the sample.
