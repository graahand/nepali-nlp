from __future__ import annotations

import argparse
import unicodedata


DEFAULT_UML_MODEL_ID = "universalml/Nepali_Tokenizer"
DEFAULT_QWEN_MODEL_ID = "Qwen/Qwen3-8B"
DEFAULT_WORD = "मानिसमा"


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


def tokenize_hf(model_id: str, word: str) -> tuple[list[int], list[str], str]:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    token_ids = tokenizer.encode(word, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    decoded = tokenizer.decode(token_ids)
    return token_ids, tokens, decoded


def tokenize_nepalitokenizers(kind: str, word: str) -> tuple[list[int], list[str], str]:
    if kind == "sentencepiece":
        from nepalitokenizers import SentencePiece

        tokenizer = SentencePiece()
    else:
        from nepalitokenizers import WordPiece

        tokenizer = WordPiece()

    encoded = tokenizer.encode(word)
    token_ids = encoded.ids
    tokens = encoded.tokens
    decoded = tokenizer.decode(token_ids)
    return token_ids, tokens, decoded


def tokenize_tiktoken(encoding_name: str, model: str | None, word: str) -> tuple[list[int], list[str], str]:
    import tiktoken

    encoding = tiktoken.encoding_for_model(model) if model else tiktoken.get_encoding(encoding_name)
    token_ids = encoding.encode(word)
    tokens = [encoding.decode([token_id]) for token_id in token_ids]
    decoded = encoding.decode(token_ids)
    return token_ids, tokens, decoded


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tokenize a single word with multiple tokenizer backends."
    )
    parser.add_argument(
        "--backend",
        default="universalml",
        choices=[
            "universalml",
            "qwen",
            "hf",
            "nepalitokenizers_wordpiece",
            "nepalitokenizers_sentencepiece",
            "tiktoken",
        ],
    )
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--word", default=DEFAULT_WORD)
    parser.add_argument("--encoding", default="o200k_base")
    parser.add_argument("--tiktoken-model", default=None)
    args = parser.parse_args()

    word = normalize_text(args.word)

    if args.backend in {"universalml", "qwen", "hf"}:
        if args.backend == "universalml":
            model_id = args.model_id or DEFAULT_UML_MODEL_ID
        elif args.backend == "qwen":
            model_id = args.model_id or DEFAULT_QWEN_MODEL_ID
        else:
            model_id = args.model_id
            if not model_id:
                raise SystemExit("--model-id is required when backend=hf")

        token_ids, tokens, decoded = tokenize_hf(model_id, word)
    elif args.backend == "nepalitokenizers_sentencepiece":
        token_ids, tokens, decoded = tokenize_nepalitokenizers("sentencepiece", word)
    elif args.backend == "nepalitokenizers_wordpiece":
        token_ids, tokens, decoded = tokenize_nepalitokenizers("wordpiece", word)
    else:
        token_ids, tokens, decoded = tokenize_tiktoken(
            args.encoding, args.tiktoken_model, word
        )

    print(f"Backend: {args.backend}")
    if args.backend in {"universalml", "qwen", "hf"}:
        print(f"Model ID: {model_id}")
    if args.backend == "tiktoken":
        if args.tiktoken_model:
            print(f"TikToken model: {args.tiktoken_model}")
        print(f"Encoding: {args.encoding}")
    print(f"Word: {word}")
    print(f"Token IDs: {token_ids}")
    print(f"Tokens: {tokens}")
    print(f"Decoded: {decoded}")


if __name__ == "__main__":
    main()
