# UniversalML Tokenizer Evaluation on IRIIS Corpus (Sample)

## Sample Configuration
- Dataset: IRIIS-RESEARCH/Nepali-Text-Corpus (train)
- Text column: Article
- Domain column: Source
- Model: universalml/Nepali_Tokenizer
- Seed: 13
- Target words: 20,000,000
- Actual words: 20,000,000
- Documents used: 84,590
- Partial last doc: True

## Fertility Rate (Tokens per Word)
| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 20000000 | 41295183 | 2.0648 | 1 | 41 | 2.0648 | 2.0 | 3.0 |
| suffix_words | 5785868 | 15378351 | 2.6579 | 1 | 31 | 2.6579 | 2.0 | 4.0 |
| halanta_words | 7141112 | 16033330 | 2.2452 | 1 | 41 | 2.2452 | 2.0 | 4.0 |
| super_suffix_words | 146214 | 446764 | 3.0555 | 2 | 10 | 3.0555 | 3.0 | 4.0 |
| chain_len_3plus | 4329 | 13493 | 3.1169 | 1 | 10 | 3.1169 | 3.0 | 5.0 |

## T/W Ratio (Document Level)
- Mean: 2.0696
- Median: 2.067510548523207
- P90: 2.241106719367589
- Min: 1.0
- Max: 3.272727272727273

## Numeral Density
| Category | Spans | Tokens | Avg Tokens/Span |
|---|---:|---:|---:|
| dev_spans | 683455 | 972083 | 1.4223 |
| ascii_spans | 0 | 0 | 0.0 |
| phone_dev | 118 | 718 | 6.0847 |
| phone_ascii | 0 | 0 | 0.0 |
| currency_dev | 14187 | 44040 | 3.1043 |
| currency_ascii | 0 | 0 | 0.0 |
| currency_mixed | 0 | 0 | 0.0 |

Note: numeral spans can overlap categories (e.g., currency spans also contain digits).

## Conjunct Integrity (Halanta Cliffhangers)
- Total halanta markers: 8838450
- Tokens ending with halanta: 1244976
- Integrity (1 - cliffhangers/total): 0.8591

## Morphological Fragmentation (Postpositions)
- Words with suffix chain: 5785868
- Words with fragmented suffix: 110165
- Fragmentation rate: 0.019

## Notes
- Suffix matching uses greedy longest-first stripping (max chain depth 6).
- Conjunct integrity flags tokens that end with a halanta as cliffhangers.
- Document ratios are computed only for full documents in the sample.
