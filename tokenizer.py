
# UNIVERSAL ML NEPALI TOKENIZER

# from transformers import AutoTokenizer

# # 1. Load the tokenizer
# model_name =  "universalml/Nepali_Tokenizer"
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# # 2. Encode text
# text = "म आज काठमाडौँ जाँदैछु।"
# inputs = tokenizer(text)

# print("Tokens IDs:", inputs["input_ids"])

# # Optional: show the actual tokens
# print("Tokens:", tokenizer.convert_ids_to_tokens(inputs["input_ids"]))

# # 3. Decode back to text
# decoded_text = tokenizer.decode(inputs["input_ids"])
# print("Decoded Text:", decoded_text)


# QWEN TOKENIZER 

# from transformers import AutoTokenizer

# # Load the latest Qwen3.5 tokenizer
# # You can also use "Qwen/Qwen3-7B" for the standard Qwen3 series
# model_id = "Qwen/Qwen3.5-9B" 
# tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# # Sample Nepali text
# nepali_text = "नमस्ते, तपाईंलाई कस्तो छ?"

# # 1. Basic Tokenization (Converting text to IDs)
# tokens = tokenizer.encode(nepali_text)
# print(f"Token IDs: {tokens}")

# # 2. See how the text is actually split (Subwords)
# subwords = [tokenizer.decode([t]) for t in tokens]
# print(f"Subword Split: {subwords}")

# # 3. Decoding back to original string
# decoded = tokenizer.decode(tokens)
# print(f"Decoded: {decoded}")

# NEPALI GRAMMAR TOKENIZER

from nepali_tokenizer import NepaliTokenizer

text = "रामले विद्यालयमा किताब पढिरहेको थियो।"
tok = NepaliTokenizer()
flat, analyses = tok.tokenize(text, hierarchical=True)
print(flat)
# ['राम', 'ले', 'विद्यालय', 'मा', 'किताब', 'पढ', 'रहेको', 'थियो', '।']
print(analyses[5])  # TokenAnalysis for verb