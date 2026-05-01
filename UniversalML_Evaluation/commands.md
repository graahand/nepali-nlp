# UniversalML
python uml_tokenize_word.py --backend universalml --word "मानिसमा"

# Qwen
python uml_tokenize_word.py --backend qwen --word "मानिसमा"

# Generic Hugging Face tokenizer
python uml_tokenize_word.py --backend hf --model-id "bert-base-multilingual-cased" --word "मानिसमा"

# nepalitokenizers
python uml_tokenize_word.py --backend nepalitokenizers_wordpiece --word "मानिसमा"
python uml_tokenize_word.py --backend nepalitokenizers_sentencepiece --word "मानिसमा"

# tiktoken
python uml_tokenize_word.py --backend tiktoken --tiktoken-model gpt-4o --word "मानिसमा"
# or explicit encoding
python uml_tokenize_word.py --backend tiktoken --encoding o200k_base --word "मानिसमा"