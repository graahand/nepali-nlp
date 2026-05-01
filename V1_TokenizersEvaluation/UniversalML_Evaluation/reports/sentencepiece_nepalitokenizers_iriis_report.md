# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: sentencepiece
- Seed: 13
- Target words: 40,000
- Actual words: 40,000
- Documents used: 168
- Partial last doc: False

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40000 | 132266 | 3.3066 | 3 | 11 | 3.3066 | 3.0 | 4.0 |
| suffix_words | 13002 | 46235 | 3.556 | 3 | 11 | 3.556 | 3.0 | 4.0 |
| halanta_words | 14370 | 48639 | 3.3848 | 3 | 11 | 3.3848 | 3.0 | 4.0 |
| super_suffix_words | 316 | 1135 | 3.5918 | 3 | 6 | 3.5918 | 4.0 | 4.0 |
| chain_len_3plus | 15 | 61 | 4.0667 | 3 | 7 | 4.0667 | 4.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 3.3014
- Median: 3.2921392476137
- P90: 3.4404761904761907
- Min: 3.074626865671642
- Max: 3.725

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 1338 | 4175 | 3.1203 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 7 | 28 | 4.0 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity
- Total conjuncts: 15907
- Fragmented conjuncts: 369
- Integrity (1 - fragmented/total): 0.9768

## Morphological Loss (Postpositions)
- Words with suffix chain: 13002
- Words with severed suffix token: 4990
- Severance rate: 0.3838

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity checks whether each conjunct appears intact in any token.
- Document ratios are computed only for full documents in the sample.
