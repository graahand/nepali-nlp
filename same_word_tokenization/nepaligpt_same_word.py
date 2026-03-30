from collections import Counter, defaultdict
from importlib import import_module
from pathlib import Path
import argparse
import unicodedata


DEFAULT_MODEL_ID = "universalml/Nepali_Tokenizer"
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
		description="Check whether repeated words tokenize the same way every time."
	)
	parser.add_argument(
		"--model-id",
		default=DEFAULT_MODEL_ID,
		help="Hugging Face model or tokenizer id.",
	)
	parser.add_argument(
		"--input-file",
		default=str(DEFAULT_INPUT_FILE),
		help="Text file containing the test set.",
	)
	parser.add_argument(
		"--show-all",
		action="store_true",
		help="Print every tokenized occurrence.",
	)
	args = parser.parse_args()

	transformers_module = import_module("transformers")
	tokenizer_cls = getattr(transformers_module, "AutoTokenizer")
	tokenizer = tokenizer_cls.from_pretrained(args.model_id, trust_remote_code=True)
	input_path = Path(args.input_file)
	words = [normalize_text(word) for word in load_words(input_path)]
	counts = Counter(words)

	seen: dict[str, list[tuple[int, tuple[int, ...], tuple[str, ...]]]] = defaultdict(list)
	token_counts: list[int] = []

	if args.show_all:
		print("Per-occurrence tokenization:\n")

	for index, word in enumerate(words, start=1):
		token_count, tokens, token_ids = tokenize_word(tokenizer, word)
		token_counts.append(token_count)
		seen[word].append((index, tuple(token_ids), tuple(tokens)))
		if args.show_all:
			print(f"{index:03d}. {word} -> {tokens} ({token_count} tokens)")

	repeated_words = {word: entries for word, entries in seen.items() if len(entries) > 1}
	inconsistent_words = {
		word: entries
		for word, entries in repeated_words.items()
		if len({entry[1] for entry in entries}) > 1
	}

	print("Summary")
	print(f"Input file: {input_path}")
	print(f"Tokenizer: {args.model_id}")
	print(f"Total word occurrences: {len(words)}")
	print(f"Unique words: {len(seen)}")
	print(f"Repeated words: {len(repeated_words)}")
	print(f"Consistent repeated words: {len(repeated_words) - len(inconsistent_words)}")
	print(f"Average tokens per occurrence: {sum(token_counts) / len(token_counts) if token_counts else 0.0:.4f}")
	print(f"Min tokens per occurrence: {min(token_counts) if token_counts else 0}")
	print(f"Max tokens per occurrence: {max(token_counts) if token_counts else 0}")

	if inconsistent_words:
		print("\nInconsistent words:")
		for word, entries in inconsistent_words.items():
			print(f"- {word}")
			for occurrence_index, token_ids, tokens in entries:
				print(f"  occurrence {occurrence_index}: {list(tokens)} -> {list(token_ids)}")
	else:
		print("\nResult: every repeated word tokenized the same way.")


if __name__ == "__main__":
	main()


