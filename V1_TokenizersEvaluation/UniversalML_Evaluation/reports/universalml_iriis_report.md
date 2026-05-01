# UniversalML Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: universalml/Nepali_Tokenizer
- Seed: 13
- Target words: 40,000
- Actual words: 40,000
- Documents used: 168
- Partial last doc: False

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40000 | 82742 | 2.0686 | 1 | 9 | 2.0686 | 2.0 | 3.0 |
| suffix_words | 13002 | 33644 | 2.5876 | 1 | 9 | 2.5876 | 2.0 | 4.0 |
| halanta_words | 14370 | 32201 | 2.2408 | 1 | 9 | 2.2408 | 2.0 | 4.0 |
| super_suffix_words | 316 | 989 | 3.1297 | 2 | 8 | 3.1297 | 3.0 | 4.0 |
| chain_len_3plus | 15 | 50 | 3.3333 | 1 | 6 | 3.3333 | 3.0 | 4.0 |

## T/W Ratio (Document Level)
- Mean: 2.0687
- Median: 2.074179832423194
- P90: 2.23728813559322
- Min: 1.75
- Max: 2.5454545454545454

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 1338 | 1930 | 1.4425 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 7 | 17 | 2.4286 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity
- Total conjuncts: 15907
- Fragmented conjuncts: 2076
- Integrity (1 - fragmented/total): 0.8695

## Morphological Loss (Postpositions)
- Words with suffix chain: 13002
- Words with severed suffix token: 9250
- Severance rate: 0.7114

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity checks whether each conjunct appears intact in any token.
- Document ratios are computed only for full documents in the sample.
