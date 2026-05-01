# Qwen Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: Qwen/Qwen3-8B
- Seed: 13
- Target words: 40,000
- Actual words: 40,000
- Documents used: 168
- Partial last doc: False

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40000 | 231572 | 5.7893 | 1 | 28 | 5.7893 | 5.0 | 9.0 |
| suffix_words | 13002 | 94656 | 7.2801 | 3 | 28 | 7.2801 | 7.0 | 10.0 |
| halanta_words | 14370 | 106102 | 7.3836 | 3 | 28 | 7.3836 | 7.0 | 11.0 |
| super_suffix_words | 316 | 2976 | 9.4177 | 6 | 20 | 9.4177 | 9.0 | 13.0 |
| chain_len_3plus | 15 | 145 | 9.6667 | 8 | 12 | 9.6667 | 10.0 | 12.0 |

## T/W Ratio (Document Level)
- Mean: 5.8227
- Median: 5.853954774365557
- P90: 6.222222222222222
- Min: 3.888888888888889
- Max: 7.181818181818182

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 1338 | 5202 | 3.8879 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 0 | 0 | 0.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 7 | 49 | 7.0 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity
- Total conjuncts: 15907
- Fragmented conjuncts: 15907
- Integrity (1 - fragmented/total): 0.0

## Morphological Loss (Postpositions)
- Words with suffix chain: 13002
- Words with severed suffix token: 0
- Severance rate: 0.0

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity checks whether each conjunct appears intact in any token.
- Document ratios are computed only for full documents in the sample.
