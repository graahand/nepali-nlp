from nepali_tokenizer import NepaliTokenizer
import unicodedata

test_set_path = "test_set.txt"
tok = NepaliTokenizer()

def load_words(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def normalize_text(text):
    return unicodedata.normalize("NFC", text)

def count_tokens_for_word(word):
    # Use flat tokenization only to avoid hierarchical analysis crash
    tokens = tok.tokenize(word)
    return len(tokens), tokens

def main():
    words = load_words(test_set_path)

    total_tokens = 0
    total_words = 0
    token_counts = []

    print("Per-word tokenization:\n")

    for word in words:
        word = normalize_text(word)
        token_count, tokens = count_tokens_for_word(word)

        total_tokens += token_count
        total_words += 1
        token_counts.append(token_count)

        print(f"{word} -> {tokens} ({token_count} tokens)")

    avg_tokens_per_word = total_tokens / total_words if total_words else 0.0

    print("\nSummary")
    print(f"Total words: {total_words}")
    print(f"Total tokens: {total_tokens}")
    print(f"Average tokens per Nepali word: {avg_tokens_per_word:.4f}")
    print(f"Min tokens per word: {min(token_counts) if token_counts else 0}")
    print(f"Max tokens per word: {max(token_counts) if token_counts else 0}")

if __name__ == "__main__":
    main()