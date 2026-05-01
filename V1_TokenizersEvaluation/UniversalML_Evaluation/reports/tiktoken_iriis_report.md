# TikToken Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model encoding: gpt-4o
- Encoding: o200k_base
- Seed: 13
- Target words: 40,000
- Actual words: 40,000
- Documents used: 168
- Partial last doc: False

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40000 | 114278 | 2.8569 | 1 | 14 | 2.8569 | 3.0 | 4.0 |
| suffix_words | 13002 | 44442 | 3.4181 | 1 | 14 | 3.4181 | 3.0 | 5.0 |
| halanta_words | 14370 | 48288 | 3.3603 | 1 | 14 | 3.3603 | 3.0 | 5.0 |
| super_suffix_words | 316 | 1210 | 3.8291 | 2 | 10 | 3.8291 | 4.0 | 5.0 |
| chain_len_3plus | 15 | 59 | 3.9333 | 3 | 6 | 3.9333 | 4.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 2.8554
- Median: 2.8565256277949778
- P90: 3.066371681415929
- Min: 2.2222222222222223
- Max: 3.6363636363636362

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 1338 | 2050 | 1.5321 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 7 | 32 | 4.5714 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity
- Total conjuncts: 15907
- Fragmented conjuncts: 4775
- Integrity (1 - fragmented/total): 0.6998

## Morphological Loss (Postpositions)
- Words with suffix chain: 13002
- Words with severed suffix token: 7897
- Severance rate: 0.6074

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity checks whether each conjunct appears intact in any token.
- Document ratios are computed only for full documents in the sample.
