# Tokenizer Evaluation Report
## Domain Word Evaluation
Loading Tokenizer: universalml/Nepali_Tokenizer

==================================================
📄 Analyzing File: morphology_suffixes.txt
==================================================

📊 Summary for morphology_suffixes.txt:
  - Total Words: 65
  - Total Tokens: 211
  - Average Tokens per Word: 3.25
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: honorifics.txt
==================================================

📊 Summary for honorifics.txt:
  - Total Words: 40
  - Total Tokens: 95
  - Average Tokens per Word: 2.38
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: literature_words.txt
==================================================

📊 Summary for literature_words.txt:
  - Total Words: 48
  - Total Tokens: 100
  - Average Tokens per Word: 2.08
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: dialectic_words.txt
==================================================

📊 Summary for dialectic_words.txt:
  - Total Words: 46
  - Total Tokens: 116
  - Average Tokens per Word: 2.52
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: loan_words.txt
==================================================

📊 Summary for loan_words.txt:
  - Total Words: 61
  - Total Tokens: 164
  - Average Tokens per Word: 2.69
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: numbers_and_symbols.txt
==================================================

📊 Summary for numbers_and_symbols.txt:
  - Total Words: 53
  - Total Tokens: 195
  - Average Tokens per Word: 3.68
  - Words with UNK tokens: 0

⚠️ Potential Issues Detected (High fragmentation or UNKs):
   [!] High fragmentation (7 tokens): '९८४१२३४५६७' -> ['▁', '९८', '४', '१२', '३', '४५', '६७']
   [!] High fragmentation (10 tokens): '+९७७-१-४१२३४५६' -> ['▁+', '९', '७७', '-', '१-', '४', '१२', '३', '४५', '६']
   [!] High fragmentation (7 tokens): '४९१ रु ५० पैसा' -> ['▁४', '९', '१▁', 'रु▁', '५०', '▁पै', 'सा']

==================================================
📄 Analyzing File: complex_conjuncts.txt
==================================================

📊 Summary for complex_conjuncts.txt:
  - Total Words: 65
  - Total Tokens: 158
  - Average Tokens per Word: 2.43
  - Words with UNK tokens: 0

⚠️ Potential Issues Detected (High fragmentation or UNKs):
   [!] High fragmentation (15 tokens): 'सिर्जनाત્મક' -> ['▁सि', 'र्ज', 'ना', '<0xE0>', '<0xAA>', '<0xA4>', '<0xE0>', '<0xAB>', '<0x8D>', '<0xE0>', '<0xAA>', '<0xAE>', '<0xE0>', '<0xAA>', '<0x95>']

==================================================
📄 Analyzing File: diacritics.txt
==================================================

📊 Summary for diacritics.txt:
  - Total Words: 44
  - Total Tokens: 108
  - Average Tokens per Word: 2.45
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: law_words.txt
==================================================

📊 Summary for law_words.txt:
  - Total Words: 48
  - Total Tokens: 119
  - Average Tokens per Word: 2.48
  - Words with UNK tokens: 0

==================================================
📄 Analyzing File: medical_words.txt
==================================================

📊 Summary for medical_words.txt:
  - Total Words: 48
  - Total Tokens: 126
  - Average Tokens per Word: 2.62
  - Words with UNK tokens: 0

##################################################
🏆 GLOBAL EVALUATION SUMMARY
##################################################
- morphology_suffixes.txt: 3.25 avg tokens/word | 0 UNKs
- honorifics.txt: 2.38 avg tokens/word | 0 UNKs
- literature_words.txt: 2.08 avg tokens/word | 0 UNKs
- dialectic_words.txt: 2.52 avg tokens/word | 0 UNKs
- loan_words.txt: 2.69 avg tokens/word | 0 UNKs
- numbers_and_symbols.txt: 3.68 avg tokens/word | 0 UNKs
- complex_conjuncts.txt: 2.43 avg tokens/word | 0 UNKs
- diacritics.txt: 2.45 avg tokens/word | 0 UNKs
- law_words.txt: 2.48 avg tokens/word | 0 UNKs
- medical_words.txt: 2.62 avg tokens/word | 0 UNKs

Overall Average: 2.69 tokens/word across 518 test cases.

## Unicode Consistency Check
=== Unicode Normalization Consistency Test ===

Word: संविधान
 NFC tokens (1): ['▁संविधान']
 NFD tokens (1): ['▁संविधान']
 ✅ Match (Consistent)

Word: किंवदन्ती
 NFC tokens (4): ['▁कि', 'ं', 'वद', 'न्ती']
 NFD tokens (4): ['▁कि', 'ं', 'वद', 'न्ती']
 ✅ Match (Consistent)

Word: अँध्यारो
 NFC tokens (4): ['▁अ', 'ँ', 'ध्य', 'ारो']
 NFD tokens (4): ['▁अ', 'ँ', 'ध्य', 'ारो']
 ✅ Match (Consistent)

Word: विज्ञान
 NFC tokens (1): ['▁विज्ञान']
 NFD tokens (1): ['▁विज्ञान']
 ✅ Match (Consistent)

Word: डँडाल्नो
 NFC tokens (4): ['▁ड', 'ँड', 'ाल्', 'नो']
 NFD tokens (4): ['▁ड', 'ँड', 'ाल्', 'नो']
 ✅ Match (Consistent)

Word: क्षमता
 NFC tokens (2): ['▁', 'क्षमता']
 NFD tokens (2): ['▁', 'क्षमता']
 ✅ Match (Consistent)

Total Inconsistent Words: 0 / 6

## Suffix Fragmentation Check
=== Suffix Fragmentation Test ===
Checking if root+suffix tokenization drastically alters the root token.

✅ OK: मानिस(['▁मानिस']) + मा(['▁मा']) -> मानिसमा(['▁मानि', 'समा'])
✅ OK: नेपाल(['▁नेपाल']) + लाई(['▁लाई']) -> नेपाललाई(['▁नेपाल', 'लाई'])
✅ OK: राम(['▁राम']) + ले(['▁ले']) -> रामले(['▁राम', 'ले'])
✅ OK: काम(['▁काम']) + को(['▁को']) -> कामको(['▁काम', 'को'])
✅ OK: किताब(['▁कि', 'ताब']) + का(['▁का']) -> किताबका(['▁कि', 'ताब', 'का'])

Summary: 0 fragmented root-suffix pairs out of 54 checked.
