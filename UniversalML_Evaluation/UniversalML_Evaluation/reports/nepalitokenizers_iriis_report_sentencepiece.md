# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Tokenizer: sentencepiece
- Seed: 13
- Target words: 4,000,000
- Actual words: 4,000,000
- Documents used: 17,057
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 4000000 | 13209470 | 3.3024 | 3 | 27 | 3.3024 | 3.0 | 4.0 |
| suffix_words | 1155515 | 4149045 | 3.5906 | 3 | 25 | 3.5906 | 3.0 | 4.0 |
| halanta_words | 1428486 | 4822602 | 3.376 | 3 | 27 | 3.376 | 3.0 | 4.0 |
| super_suffix_words | 28558 | 101436 | 3.5519 | 3 | 10 | 3.5519 | 3.0 | 4.0 |
| chain_len_3plus | 803 | 3227 | 4.0187 | 3 | 8 | 4.0187 | 4.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 3.3008
- Median: 3.2845849802371543
- P90: 3.4404761904761907
- Min: 3.0
- Max: 4.446969696969697

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 136937 | 427098 | 3.1189 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 20 | 140 | 7.0 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 2964 | 12563 | 4.2385 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 1767739
- Tokens ending with halanta: 82628
- Integrity (1 - cliffhangers/total): 0.9533

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 1155515
- Words with fragmented suffix: 69
- Fragmentation rate: 0.0001

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
