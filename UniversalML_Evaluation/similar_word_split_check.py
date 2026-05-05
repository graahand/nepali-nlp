from __future__ import annotations

import argparse
import csv
import difflib
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from datasets import load_dataset


DEFAULT_DATASET = "IRIIS-RESEARCH/Nepali-Text-Corpus"
DEFAULT_WORD = "मानिसमा"
DEFAULT_UML_MODEL_ID = "universalml/Nepali_Tokenizer"
DEFAULT_QWEN_MODEL_ID = "Qwen/Qwen3-8B"

STRIP_CHARS = ".,?!\u0964\u0965'\"()[]{}:;-\u2013\u2014"

ALL_SUFFIXES = sorted(
    [
        "गरिरहेकाले",
        "गरिरहेकोले",
        "गरिरहेको",
        "गरिरहेका",
        "भइसकेकाले",
        "भइसकेको",
        "गरिसकेकाले",
        "गरिसकेको",
        "हुँदैगर्दा",
        "गर्दैगर्दा",
        "हरुलाई",
        "हरुबाट",
        "हरुसँग",
        "हरुसँगै",
        "हरुको",
        "हरुका",
        "हरुकी",
        "हरुले",
        "हरुमा",
        "हरुमात्र",
        "हरूलाई",
        "हरूबाट",
        "हरूसँग",
        "हरूको",
        "हरूका",
        "हरूकी",
        "हरूले",
        "हरूमा",
        "इरहेको",
        "इसकेको",
        "इरहेका",
        "इसकेका",
        "दैछन्",
        "दैछ",
        "दैथ्यो",
        "दैथिए",
        "नुभयो",
        "नुभए",
        "नुहुन्छ",
        "नुपर्छ",
        "नुपर्ने",
        "एकोले",
        "एकोमा",
        "एकोका",
        "एकाले",
        "हरू",
        "हरु",
        "सँगसँगै",
        "सँगै",
        "सँग",
        "भन्दा",
        "देखि",
        "सम्म",
        "तिर",
        "भित्र",
        "माथि",
        "तल",
        "अगि",
        "पछि",
        "नेर",
        "थरी",
        "बाट",
        "लाई",
        "मात्र",
        "नै",
        "चाहिँ",
        "मा",
        "ले",
        "को",
        "का",
        "की",
        "पनि",
        "नि",
        "त",
    ],
    key=len,
    reverse=True,
)


@dataclass
class TokenizationResult:
    token_ids: list[int]
    tokens: list[str]
    decoded: str
    clean_tokens: list[str]


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", str(text)).strip()


def extract_words(text: str) -> list[str]:
    words: list[str] = []
    for raw in text.split():
        cleaned = raw.strip(STRIP_CHARS)
        if cleaned:
            words.append(cleaned)
    return words


def strip_suffix_chain(word: str, suffix_list: list[str]) -> tuple[str, list[str]]:
    chain: list[str] = []
    current = word
    for _ in range(6):
        if len(current) <= 3:
            break
        matched = False
        for suffix in suffix_list:
            if current.endswith(suffix):
                stem_len = len(current) - len(suffix)
                if stem_len < 3:
                    continue
                chain.append(suffix)
                current = current[: -len(suffix)]
                matched = True
                break
        if not matched:
            break
    return current, chain


def normalize_token(token: str) -> str:
    for prefix in ("##", "▁", "Ġ", "▊", "Ċ", "▌"):
        if token.startswith(prefix):
            token = token[len(prefix) :]
            break
    return token.lstrip()


def tokens_fragmented(tokens: list[str], piece: str) -> bool:
    if piece in tokens:
        return False
    for start in range(len(tokens)):
        combined = ""
        for end in range(start, len(tokens)):
            combined += tokens[end]
            if len(combined) > len(piece):
                break
            if combined == piece and end > start:
                return True
    return False


def tokenize_word(args: argparse.Namespace, word: str) -> TokenizationResult:
    if args.backend in {"universalml", "qwen", "hf"}:
        from transformers import AutoTokenizer

        model_id = args.model_id
        if args.backend == "universalml":
            model_id = model_id or DEFAULT_UML_MODEL_ID
        elif args.backend == "qwen":
            model_id = model_id or DEFAULT_QWEN_MODEL_ID
        if not model_id:
            raise SystemExit("--model-id is required for backend=hf")

        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        token_ids = tokenizer.encode(word, add_special_tokens=False)
        tokens = tokenizer.convert_ids_to_tokens(token_ids)
        decoded = tokenizer.decode(token_ids)
    elif args.backend == "nepalitokenizers_wordpiece":
        from nepalitokenizers import WordPiece

        tokenizer = WordPiece()
        encoded = tokenizer.encode(word)
        token_ids = encoded.ids
        tokens = encoded.tokens
        decoded = tokenizer.decode(token_ids)
    elif args.backend == "nepalitokenizers_sentencepiece":
        from nepalitokenizers import SentencePiece

        tokenizer = SentencePiece()
        encoded = tokenizer.encode(word)
        token_ids = encoded.ids
        tokens = encoded.tokens
        decoded = tokenizer.decode(token_ids)
    else:
        import tiktoken

        if args.tiktoken_model:
            encoding = tiktoken.encoding_for_model(args.tiktoken_model)
        else:
            encoding = tiktoken.get_encoding(args.encoding)
        token_ids = encoding.encode(word)
        tokens = [encoding.decode([token_id]) for token_id in token_ids]
        decoded = encoding.decode(token_ids)

    clean_tokens = [normalize_token(tok) for tok in tokens if tok]
    clean_tokens = [tok for tok in clean_tokens if tok]

    return TokenizationResult(
        token_ids=token_ids,
        tokens=tokens,
        decoded=decoded,
        clean_tokens=clean_tokens,
    )


def iter_dataset(args: argparse.Namespace) -> Iterable[dict]:
    dataset = load_dataset(args.dataset, split=args.split, streaming=args.streaming)
    if args.streaming:
        return dataset
    if args.shuffle:
        dataset = dataset.shuffle(seed=args.seed)
    return dataset


def score_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def should_keep_candidate(word: str, target: str, target_root: str, target_chain: list[str], min_sim: float) -> bool:
    if word == target:
        return False
    if score_similarity(word, target) >= min_sim:
        return True
    if target_chain and any(word.endswith(suffix) for suffix in target_chain):
        return True
    if target_root and word.startswith(target_root):
        return True
    return False


def analyze_word(word: str, token_result: TokenizationResult) -> dict:
    root, chain = strip_suffix_chain(word, ALL_SUFFIXES)
    suffixes = list(chain)

    root_intact = root in token_result.clean_tokens if root else False
    root_fragmented = tokens_fragmented(token_result.clean_tokens, root) if root else False

    suffix_intact = any(suffix in token_result.clean_tokens for suffix in suffixes)
    suffix_fragmented = any(
        tokens_fragmented(token_result.clean_tokens, suffix) for suffix in suffixes
    )

    return {
        "root": root,
        "suffixes": "+".join(suffixes) if suffixes else "",
        "root_status": "intact" if root_intact else "fragmented" if root_fragmented else "missing",
        "suffix_status": "intact" if suffix_intact else "fragmented" if suffix_fragmented else "missing",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find words similar to a target and inspect root/suffix tokenization."
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--split", default="train")
    parser.add_argument("--streaming", action="store_true")
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--max-words", type=int, default=200000)
    parser.add_argument("--max-matches", type=int, default=50)
    parser.add_argument("--min-similarity", type=float, default=0.7)
    parser.add_argument("--word", default=DEFAULT_WORD)
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
    parser.add_argument("--encoding", default="o200k_base")
    parser.add_argument("--tiktoken-model", default=None)
    parser.add_argument("--output", default=None, help="Optional CSV output path")
    args = parser.parse_args()

    target = normalize_text(args.word)
    target_root, target_chain = strip_suffix_chain(target, ALL_SUFFIXES)

    matches: list[dict] = []
    seen: set[str] = set()
    total_words = 0

    for row in iter_dataset(args):
        text = row.get("Article") or row.get("text") or row.get("Text")
        if not text:
            continue
        text = normalize_text(text)
        words = extract_words(text)
        for word in words:
            total_words += 1
            if total_words > args.max_words:
                break
            if word in seen:
                continue
            if not should_keep_candidate(word, target, target_root, target_chain, args.min_similarity):
                continue

            seen.add(word)
            token_result = tokenize_word(args, word)
            analysis = analyze_word(word, token_result)
            similarity = score_similarity(word, target)

            matches.append(
                {
                    "word": word,
                    "similarity": round(similarity, 4),
                    "root": analysis["root"],
                    "suffixes": analysis["suffixes"],
                    "root_status": analysis["root_status"],
                    "suffix_status": analysis["suffix_status"],
                    "tokens": "|".join(token_result.tokens),
                    "clean_tokens": "|".join(token_result.clean_tokens),
                }
            )

            if len(matches) >= args.max_matches:
                break
        if total_words > args.max_words or len(matches) >= args.max_matches:
            break

    print(f"Target: {target}")
    print(f"Root: {target_root} | Suffixes: {'+'.join(target_chain) if target_chain else 'None'}")
    print(f"Scanned words: {total_words}")
    print(f"Matches: {len(matches)}")

    for match in matches:
        print(
            f"{match['word']} | sim={match['similarity']} | root={match['root_status']} | "
            f"suffix={match['suffix_status']} | tokens={match['tokens']}"
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "word",
                    "similarity",
                    "root",
                    "suffixes",
                    "root_status",
                    "suffix_status",
                    "tokens",
                    "clean_tokens",
                ],
            )
            writer.writeheader()
            writer.writerows(matches)


if __name__ == "__main__":
    main()
