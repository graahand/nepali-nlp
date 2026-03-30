from __future__ import annotations

import argparse
from importlib import import_module
import sys
import unicodedata


DEFAULT_MODEL_ID = "universalml/Nepali_Tokenizer"


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


def tokenize_text(tokenizer, text: str) -> tuple[list[str], list[int]]:
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    return tokens, token_ids


def read_input_text() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    print("Paste Devanagari text below. Finish with an empty line and press Enter:")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)

    return " ".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tokenize pasted Devanagari text and report average token statistics."
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Hugging Face model or tokenizer id.",
    )
    parser.add_argument(
        "--text",
        help="Devanagari text to tokenize. If omitted, text is read from stdin or typed interactively.",
    )
    args = parser.parse_args()

    transformers_module = import_module("transformers")
    tokenizer_cls = getattr(transformers_module, "AutoTokenizer")
    tokenizer = tokenizer_cls.from_pretrained(args.model_id, trust_remote_code=True)

    text = args.text if args.text is not None else read_input_text()
    text = normalize_text(text)

    if not text:
        print("No input text provided.")
        return

    words = text.split()
    total_tokens = 0
    token_counts: list[int] = []

    print("Tokenization:\n")
    print(f"Input text: {text}\n")

    for index, word in enumerate(words, start=1):
        tokens, token_ids = tokenize_text(tokenizer, word)
        token_count = len(token_ids)
        total_tokens += token_count
        token_counts.append(token_count)
        print(f"{index:03d}. {word} -> {tokens} ({token_count} tokens)")

    total_words = len(words)
    avg_tokens_per_word = total_tokens / total_words if total_words else 0.0
    overall_tokens, overall_token_ids = tokenize_text(tokenizer, text)

    print("\nSummary")
    print(f"Total words: {total_words}")
    print(f"Total tokens across words: {total_tokens}")
    print(f"Average tokens per word: {avg_tokens_per_word:.4f}")
    print(f"Min tokens per word: {min(token_counts) if token_counts else 0}")
    print(f"Max tokens per word: {max(token_counts) if token_counts else 0}")
    print(f"Tokens for full text: {overall_tokens}")
    print(f"Full-text token IDs: {overall_token_ids}")


if __name__ == "__main__":
    main()