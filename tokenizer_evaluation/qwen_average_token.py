from collections import Counter, defaultdict
from importlib import import_module
from pathlib import Path
import argparse
import unicodedata


DEFAULT_MODEL_ID = "Qwen/Qwen3.5-9B"
DEFAULT_INPUT_FILE = Path(__file__).with_name("test_set.txt")


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def load_words(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [word for word in text.split() if word.strip()]


def tokenize_word(tokenizer, word: str) -> tuple[int, list[str], list[int]]:
    token_ids = tokenizer.encode(word, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    return len(token_ids), tokens, token_ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure tokenization density and summarize repeated-word behavior."
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Hugging Face model or tokenizer id.",
    )
    parser.add_argument(
        "--input-file",
        default=str(DEFAULT_INPUT_FILE),
        help="Text file containing the Nepali evaluation text.",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Print every word tokenization instead of only the summary.",
    )
    args = parser.parse_args()

    transformers_module = import_module("transformers")
    tokenizer_cls = getattr(transformers_module, "AutoTokenizer")
    tokenizer = tokenizer_cls.from_pretrained(args.model_id, trust_remote_code=True)

    input_path = Path(args.input_file)
    words = [normalize_text(word) for word in load_words(input_path)]
    counts = Counter(words)

    token_counts: list[int] = []
    repeated_examples: dict[str, tuple[int, list[str], list[int]]] = {}
    repeated_inconsistencies: dict[str, list[tuple[int, tuple[int, ...]]]] = defaultdict(list)

    if args.show_all:
        print("Per-word tokenization:\n")

    for index, word in enumerate(words, start=1):
        token_count, tokens, token_ids = tokenize_word(tokenizer, word)
        token_counts.append(token_count)

        if counts[word] > 1:
            repeated_inconsistencies[word].append((index, tuple(token_ids)))
            repeated_examples.setdefault(word, (token_count, tokens, token_ids))

        if args.show_all:
            print(f"{index:03d}. {word} -> {tokens} ({token_count} tokens)")

    total_occurrences = len(words)
    unique_words = len(counts)
    repeated_words = sum(1 for word, freq in counts.items() if freq > 1)
    avg_tokens_per_occurrence = sum(token_counts) / total_occurrences if total_occurrences else 0.0
    avg_tokens_per_unique_word = (
        sum(tokenize_word(tokenizer, word)[0] for word in counts) / unique_words if unique_words else 0.0
    )

    print("Summary")
    print(f"Input file: {input_path}")
    print(f"Tokenizer: {args.model_id}")
    print(f"Total word occurrences: {total_occurrences}")
    print(f"Unique words: {unique_words}")
    print(f"Repeated words: {repeated_words}")
    print(f"Average tokens per occurrence: {avg_tokens_per_occurrence:.4f}")
    print(f"Average tokens per unique word: {avg_tokens_per_unique_word:.4f}")
    print(f"Min tokens per occurrence: {min(token_counts) if token_counts else 0}")
    print(f"Max tokens per occurrence: {max(token_counts) if token_counts else 0}")

    if repeated_inconsistencies:
        print("\nRepeated-word check")
        print("Tokenization is deterministic, but repeated-word entries are grouped below:")
        for word, entries in repeated_inconsistencies.items():
            first_count, first_tokens, _ = repeated_examples[word]
            print(f"- {word}: {len(entries)} occurrences, example tokens {first_tokens} ({first_count} tokens)")
    else:
        print("\nRepeated-word check: no repeated words found.")

if __name__ == "__main__":
    main()
    