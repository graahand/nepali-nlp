from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from tokenizers import Tokenizer


DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
WORD_RE = re.compile(r"\S+")


@dataclass
class EvaluationResult:
    total_words: int
    total_tokens: int
    avg_tokens_per_word: float


def load_tokenizer(tokenizer_file: str) -> Tokenizer:
    """Load a fast tokenizer directly from a tokenizer.json file."""
    return Tokenizer.from_file(tokenizer_file)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_nepali_word(token: str) -> bool:
    """Return True if the token contains at least one Devanagari character."""
    return bool(DEVANAGARI_RE.search(token))


def load_corpus_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def count_nepali_words(text: str) -> int:
    words = (match.group(0) for match in WORD_RE.finditer(text))
    return sum(1 for word in words if is_nepali_word(word))


def evaluate_average_tokens_per_word(tokenizer, text: str) -> EvaluationResult:
    text = normalize_text(text)
    total_words = count_nepali_words(text)
    token_ids = tokenizer.encode(text).ids
    total_tokens = len(token_ids)
    avg_tokens_per_word = total_tokens / total_words if total_words else 0.0
    return EvaluationResult(
        total_words=total_words,
        total_tokens=total_tokens,
        avg_tokens_per_word=avg_tokens_per_word,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure average tokens per Nepali word for a tokenizer."
    )
    parser.add_argument(
        "--tokenizer-file",
        default="tokenizer.json",
        help="Path to tokenizer.json",
    )
    parser.add_argument(
        "--input-file",
        default="tokenizer_evaluation/test_set.txt",
        help="Path to the Nepali test set text file",
    )
    args = parser.parse_args()

    tokenizer = load_tokenizer(args.tokenizer_file)
    corpus_text = load_corpus_text(args.input_file)
    result = evaluate_average_tokens_per_word(tokenizer, corpus_text)

    print(f"Input file: {args.input_file}")
    print(f"Tokenizer file: {args.tokenizer_file}")
    print(f"Nepali words: {result.total_words}")
    print(f"Total tokens: {result.total_tokens}")
    print(f"Average tokens per Nepali word: {result.avg_tokens_per_word:.4f}")


if __name__ == "__main__":
    main()
