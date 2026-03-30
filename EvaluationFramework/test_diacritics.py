from tokenizer_eval_utils import get_tokenizer, analyze_file

if __name__ == "__main__":
    tokenizer = get_tokenizer()
    analyze_file(tokenizer, "diacritics.txt")
