# Nepali Tokenizer Evaluation Framework

This framework provides an automated suite to evaluate the tokenization performance, density, and correctness of Nepali text tokenizers (e.g., `universalml/Nepali_Tokenizer`).

## Folder Structure

- `evaluate_tokenizer.py`: Main script to analyze how the tokenizer behaves on various test subsets.
- `EvalTest/`: Contains specific evaluation sets targeted at different aspects of the Nepali language.
  - `complex_conjuncts.txt`: Words containing complex Devanagari conjuncts, halantas, and ligatures to test if the tokenizer illegally splits graphemes.
  - `loan_words.txt`: English loan words written in Devanagari (e.g., कम्प्युटर, इन्टरनेट) to see if it handles modern transliterations smoothly.
  - `morphology_suffixes.txt`: Highly agglutinated Nepali words (e.g., भइसकेकोछ, मानिसहरुलाई) to test chunking of roots vs suffixes.
  - `numbers_and_symbols.txt`: Numbers, dates, percentages, and symbol combinations natively written in Devanagari scripts and mix-ups.

## Usage

Run the standard evaluation:

```bash
cd /home/graahand/Qwen-VL_LoRA_Finetuning/Nlpnepali/EvaluationFramework
python evaluate_tokenizer.py --model-id "universalml/Nepali_Tokenizer"
```

To see every single word and how it is tokenized (for debugging specific failures):

```bash
python evaluate_tokenizer.py --verbose
```

## What to look for
1. **High Tokenization Length (Fragmentation):** If a standard Nepali word is being broken into > 6 tokens, the tokenizer might not have learned that sequence well.
2. **UNK Tokens:** If a rare symbol or conjunct results in an `[UNK]` token, it destroys meaning.
3. **Invalid Breakages:** Check if zero-width joiners / Halantas (`्`) are split independently from bounding letters. This breaks display algorithms and structural meaning for LLMs.