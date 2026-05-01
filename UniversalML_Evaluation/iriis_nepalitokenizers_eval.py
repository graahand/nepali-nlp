from __future__ import annotations

import argparse
import csv
import os
import re
import statistics
import unicodedata
from dataclasses import dataclass, field

from datasets import load_dataset
from nepalitokenizers import SentencePiece, WordPiece


DEFAULT_DATASET = "IRIIS-RESEARCH/Nepali-Text-Corpus"
DEFAULT_OUTPUT_DIR = "UniversalML_Evaluation"
DEFAULT_TOKENIZER = "wordpiece"

STRIP_CHARS = ".,?!\u0964\u0965'\"()[]{}:;-\u2013\u2014"

# ─────────────────────────────────────────────────────────────────────────────
# A1 — Morphological inventory (from IRIIS linguistic_audit.py)
# ─────────────────────────────────────────────────────────────────────────────

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

SUPER_SUFFIX_CANDIDATES = [
    "हरुलाई",
    "हरुबाट",
    "हरुसँग",
    "हरुको",
    "हरुले",
    "हरुमा",
    "भइसकेको",
    "भइसकेकाले",
    "गरिरहेको",
    "गरिरहेकाले",
    "गरिसकेको",
    "गरिसकेकाले",
    "नुपर्छ",
    "नुहुन्छ",
    "नुभयो",
    "दैछन्",
    "दैछ",
    "एकोले",
    "एकाले",
]

# ─────────────────────────────────────────────────────────────────────────────
# A2 — Conjunct inventory
# ─────────────────────────────────────────────────────────────────────────────

HALANTA = "\u094D"

CONJUNCT_RE = re.compile(
    r"(?:[\u0915-\u0939\u0958-\u095F]" r"\u094D" r")+" r"[\u0915-\u0939\u0958-\u095F]"
)

# ─────────────────────────────────────────────────────────────────────────────
# A3 — Numeral inventory
# ─────────────────────────────────────────────────────────────────────────────

DEV_SPAN_RE = re.compile(r"[०-९]+")
ASCII_SPAN_RE = re.compile(r"[0-9]+")
PHONE_DEV_RE = re.compile(r"(?<![०-९])[९८][०-९]{8,9}(?![०-९])")
PHONE_ASC_RE = re.compile(r"(?<![0-9])(?:98|97|96|01)[0-9]{7,8}(?![0-9])")
CURRENCY_RE = re.compile(
    r"(?:रु\.?\s*|रुपैयाँ\s*|Rs\.?\s*|\$|£|¥|€)"
    r"[०-९0-9][०-९0-9,\.]*"
    r"|[०-९0-9][०-९0-9,\.]*\s*(?:रुपैयाँ|रुपया)"
)


@dataclass
class TokenStats:
    words: int = 0
    tokens: int = 0
    token_counts: list[int] = field(default_factory=list)

    def add(self, token_count: int) -> None:
        self.words += 1
        self.tokens += token_count
        self.token_counts.append(token_count)

    def summary(self) -> dict:
        if not self.token_counts:
            return {
                "words": 0,
                "tokens": 0,
                "tpw": 0.0,
                "min": 0,
                "max": 0,
                "mean": 0.0,
                "median": 0.0,
                "p90": 0.0,
            }

        counts_sorted = sorted(self.token_counts)
        n = len(counts_sorted)
        p90_index = int(0.9 * (n - 1))
        return {
            "words": self.words,
            "tokens": self.tokens,
            "tpw": round(self.tokens / self.words, 4),
            "min": counts_sorted[0],
            "max": counts_sorted[-1],
            "mean": round(sum(counts_sorted) / n, 4),
            "median": float(statistics.median(counts_sorted)),
            "p90": float(counts_sorted[p90_index]),
        }


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", str(text)).strip()


def resolve_text_column(columns: list[str], preferred: str | None) -> str:
    if preferred and preferred in columns:
        return preferred
    lower_map = {col.lower(): col for col in columns}
    for key in ("article", "text", "content", "body"):
        if key in lower_map:
            return lower_map[key]
    for col in columns:
        if col.lower() not in {"index", "id"}:
            return col
    return columns[0]


def resolve_domain_column(columns: list[str], preferred: str | None) -> str | None:
    if preferred and preferred in columns:
        return preferred
    lower_map = {col.lower(): col for col in columns}
    for key in ("source", "domain", "url"):
        if key in lower_map:
            return lower_map[key]
    return None


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
            return token[len(prefix) :]
    return token


def extract_words(text: str) -> list[str]:
    words: list[str] = []
    for raw in text.split():
        cleaned = raw.strip(STRIP_CHARS)
        if cleaned:
            words.append(cleaned)
    return words


def classify_currency_span(span: str) -> str:
    has_dev = any("०" <= ch <= "९" for ch in span)
    has_ascii = any("0" <= ch <= "9" for ch in span)
    if has_dev and has_ascii:
        return "currency_mixed"
    if has_dev:
        return "currency_dev"
    if has_ascii:
        return "currency_ascii"
    return "currency_other"


def is_suffix_fragmented(tokens: list[str], suffix: str) -> bool:
    if suffix in tokens:
        return False
    for start in range(len(tokens)):
        combined = ""
        for end in range(start, len(tokens)):
            combined += tokens[end]
            if len(combined) > len(suffix):
                break
            if combined == suffix and end > start:
                return True
    return False


def build_tokenizer(kind: str):
    if kind == "sentencepiece":
        return SentencePiece()
    return WordPiece()


def encode_tokens(tokenizer, text: str) -> tuple[list[int], list[str]]:
    encoded = tokenizer.encode(text)
    return encoded.ids, encoded.tokens


def evaluate_sample(args: argparse.Namespace) -> dict:
    tokenizer = build_tokenizer(args.tokenizer)
    dataset = load_dataset(args.dataset, split=args.split)
    if args.shuffle:
        dataset = dataset.shuffle(seed=args.seed)

    text_col = resolve_text_column(dataset.column_names, args.text_col)
    domain_col = resolve_domain_column(dataset.column_names, args.domain_col)

    subset_stats = {
        "all": TokenStats(),
        "suffix_words": TokenStats(),
        "halanta_words": TokenStats(),
        "super_suffix_words": TokenStats(),
        "chain_len_3plus": TokenStats(),
    }

    doc_ratios: list[float] = []
    total_docs = 0
    used_docs = 0
    partial_last_doc = False

    morphological_total = 0
    morphological_severed = 0

    halanta_total = 0
    halanta_cliffhangers = 0

    numeral_stats = {
        "dev_spans": {"spans": 0, "tokens": 0, "token_counts": []},
        "ascii_spans": {"spans": 0, "tokens": 0, "token_counts": []},
        "phone_dev": {"spans": 0, "tokens": 0, "token_counts": []},
        "phone_ascii": {"spans": 0, "tokens": 0, "token_counts": []},
        "currency_dev": {"spans": 0, "tokens": 0, "token_counts": []},
        "currency_ascii": {"spans": 0, "tokens": 0, "token_counts": []},
        "currency_mixed": {"spans": 0, "tokens": 0, "token_counts": []},
    }

    def update_numeral(stat_key: str, span: str) -> None:
        token_ids, _tokens = encode_tokens(tokenizer, span)
        token_count = len(token_ids)
        entry = numeral_stats[stat_key]
        entry["spans"] += 1
        entry["tokens"] += token_count
        entry["token_counts"].append(token_count)

    def apply_priority_numerals(text: str) -> None:
        mask = list(text)

        def mask_span(start: int, end: int) -> None:
            for index in range(start, end):
                mask[index] = " "

        for match in PHONE_DEV_RE.finditer(text):
            update_numeral("phone_dev", match.group())
            mask_span(match.start(), match.end())
        for match in PHONE_ASC_RE.finditer(text):
            update_numeral("phone_ascii", match.group())
            mask_span(match.start(), match.end())
        for match in CURRENCY_RE.finditer(text):
            stat_key = classify_currency_span(match.group())
            if stat_key in numeral_stats:
                update_numeral(stat_key, match.group())
                mask_span(match.start(), match.end())

        masked_text = "".join(mask)
        for match in DEV_SPAN_RE.finditer(masked_text):
            update_numeral("dev_spans", match.group())
        for match in ASCII_SPAN_RE.finditer(masked_text):
            update_numeral("ascii_spans", match.group())

    total_words = 0

    for row in dataset:
        total_docs += 1
        text = row.get(text_col, "")
        if not text:
            continue
        text = normalize_text(text)
        if not text:
            continue

        words = extract_words(text)
        if not words:
            continue

        if total_words + len(words) <= args.target_words:
            take_words = words
            full_doc = True
        else:
            remaining = args.target_words - total_words
            if remaining <= 0:
                break
            take_words = words[:remaining]
            full_doc = False
            partial_last_doc = True

        if full_doc:
            used_docs += 1
            doc_word_count = 0
            doc_token_count = 0

            apply_priority_numerals(text)
        else:
            doc_word_count = 0
            doc_token_count = 0

        for word in take_words:
            token_ids, tokens = encode_tokens(tokenizer, word)
            token_count = len(token_ids)
            subset_stats["all"].add(token_count)

            doc_word_count += 1
            doc_token_count += token_count
            total_words += 1

            tokens_clean = [normalize_token(tok) for tok in tokens if tok]
            tokens_clean = [tok for tok in tokens_clean if tok]

            _stem, chain = strip_suffix_chain(word, ALL_SUFFIXES)
            if chain:
                subset_stats["suffix_words"].add(token_count)
                morphological_total += 1
                if any(is_suffix_fragmented(tokens_clean, suffix) for suffix in chain):
                    morphological_severed += 1
                if len(chain) >= 3:
                    subset_stats["chain_len_3plus"].add(token_count)
                if any(word.endswith(suf) for suf in SUPER_SUFFIX_CANDIDATES):
                    subset_stats["super_suffix_words"].add(token_count)

            if HALANTA in word:
                subset_stats["halanta_words"].add(token_count)
                halanta_total += word.count(HALANTA)
                halanta_cliffhangers += sum(
                    1 for tok in tokens_clean if tok.endswith(HALANTA)
                )

            if total_words >= args.target_words:
                break

        if full_doc and doc_word_count:
            doc_ratios.append(doc_token_count / doc_word_count)

        if total_words >= args.target_words:
            break

        if args.max_docs and used_docs >= args.max_docs:
            break

    def numeral_summary(stat_key: str) -> dict:
        entry = numeral_stats[stat_key]
        counts = entry["token_counts"]
        avg = round(sum(counts) / len(counts), 4) if counts else 0.0
        return {"spans": entry["spans"], "tokens": entry["tokens"], "avg_tps": avg}

    return {
        "tokenizer": args.tokenizer,
        "dataset": args.dataset,
        "split": args.split,
        "seed": args.seed,
        "target_words": args.target_words,
        "actual_words": total_words,
        "documents_seen": total_docs,
        "documents_used": used_docs,
        "partial_last_doc": partial_last_doc,
        "text_col": text_col,
        "domain_col": domain_col,
        "subset_stats": {key: stats.summary() for key, stats in subset_stats.items()},
        "morphological_total": morphological_total,
        "morphological_severed": morphological_severed,
        "total_conjuncts": halanta_total,
        "fragmented_conjuncts": halanta_cliffhangers,
        "doc_ratios": doc_ratios,
        "numeral_summary": {
            "dev_spans": numeral_summary("dev_spans"),
            "ascii_spans": numeral_summary("ascii_spans"),
            "phone_dev": numeral_summary("phone_dev"),
            "phone_ascii": numeral_summary("phone_ascii"),
            "currency_dev": numeral_summary("currency_dev"),
            "currency_ascii": numeral_summary("currency_ascii"),
            "currency_mixed": numeral_summary("currency_mixed"),
        },
    }


def write_csv_reports(result: dict, output_dir: str) -> None:
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    suffix = result["tokenizer"]
    subset_path = os.path.join(data_dir, f"metrics_summary_nepalitokenizers_{suffix}.csv")
    with open(subset_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "subset",
                "words",
                "tokens",
                "tpw",
                "min_tokens",
                "max_tokens",
                "mean_tokens",
                "median_tokens",
                "p90_tokens",
            ]
        )
        for subset, stats in result["subset_stats"].items():
            writer.writerow(
                [
                    subset,
                    stats["words"],
                    stats["tokens"],
                    stats["tpw"],
                    stats["min"],
                    stats["max"],
                    stats["mean"],
                    stats["median"],
                    stats["p90"],
                ]
            )

    numeral_path = os.path.join(data_dir, f"numeral_metrics_nepalitokenizers_{suffix}.csv")
    with open(numeral_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["category", "spans", "tokens", "avg_tokens_per_span"])
        for category, stats in result["numeral_summary"].items():
            writer.writerow([category, stats["spans"], stats["tokens"], stats["avg_tps"]])

    doc_path = os.path.join(data_dir, f"doc_tw_summary_nepalitokenizers_{suffix}.csv")
    ratios = result["doc_ratios"]
    ratios_sorted = sorted(ratios)
    if ratios_sorted:
        n = len(ratios_sorted)
        p90_index = int(0.9 * (n - 1))
        doc_summary = {
            "docs": n,
            "mean": round(sum(ratios_sorted) / n, 4),
            "median": float(statistics.median(ratios_sorted)),
            "p90": float(ratios_sorted[p90_index]),
            "min": ratios_sorted[0],
            "max": ratios_sorted[-1],
        }
    else:
        doc_summary = {"docs": 0, "mean": 0.0, "median": 0.0, "p90": 0.0, "min": 0.0, "max": 0.0}

    with open(doc_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["docs", "mean", "median", "p90", "min", "max"])
        writer.writerow(
            [
                doc_summary["docs"],
                doc_summary["mean"],
                doc_summary["median"],
                doc_summary["p90"],
                doc_summary["min"],
                doc_summary["max"],
            ]
        )


def write_markdown_report(result: dict, output_dir: str) -> None:
    report_dir = os.path.join(output_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)
    suffix = result["tokenizer"]
    report_path = os.path.join(report_dir, f"nepalitokenizers_iriis_report_{suffix}.md")

    ratios = result["doc_ratios"]
    if ratios:
        ratios_sorted = sorted(ratios)
        n = len(ratios_sorted)
        p90_index = int(0.9 * (n - 1))
        doc_mean = round(sum(ratios_sorted) / n, 4)
        doc_median = float(statistics.median(ratios_sorted))
        doc_p90 = float(ratios_sorted[p90_index])
        doc_min = ratios_sorted[0]
        doc_max = ratios_sorted[-1]
    else:
        doc_mean = doc_median = doc_p90 = doc_min = doc_max = 0.0

    morph_total = result["morphological_total"]
    morph_severed = result["morphological_severed"]
    morph_rate = round(morph_severed / morph_total, 4) if morph_total else 0.0

    conj_total = result["total_conjuncts"]
    conj_fragmented = result["fragmented_conjuncts"]
    conj_integrity = round(1 - (conj_fragmented / conj_total), 4) if conj_total else 0.0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Nepali Tokenizers Evaluation on IRIIS Corpus (Sample)\n\n")
        f.write("## Sample Configuration\n")
        f.write(f"- Dataset: {result['dataset']} ({result['split']})\n")
        f.write(f"- Text column: {result['text_col']}\n")
        if result["domain_col"]:
            f.write(f"- Domain column: {result['domain_col']}\n")
        f.write(f"- Tokenizer: {result['tokenizer']}\n")
        f.write(f"- Seed: {result['seed']}\n")
        f.write(f"- Target words: {result['target_words']:,}\n")
        f.write(f"- Actual words: {result['actual_words']:,}\n")
        f.write(f"- Documents used: {result['documents_used']:,}\n")
        f.write(f"- Partial last doc: {result['partial_last_doc']}\n\n")

        f.write("## Fertility Rate (Tokens per Word)\n")
        f.write("| Subset | Words | Tokens | TPW | Min | Max | Mean | Median | P90 |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for subset, stats in result["subset_stats"].items():
            f.write(
                f"| {subset} | {stats['words']} | {stats['tokens']} | {stats['tpw']} | {stats['min']} | {stats['max']} | {stats['mean']} | {stats['median']} | {stats['p90']} |\n"
            )
        f.write("\n")

        f.write("## T/W Ratio (Document Level)\n")
        f.write(f"- Mean: {doc_mean}\n")
        f.write(f"- Median: {doc_median}\n")
        f.write(f"- P90: {doc_p90}\n")
        f.write(f"- Min: {doc_min}\n")
        f.write(f"- Max: {doc_max}\n\n")

        f.write("## Numeral Density\n")
        f.write("| Category | Spans | Tokens | Avg Tokens/Span |\n")
        f.write("|---|---:|---:|---:|\n")
        for category, stats in result["numeral_summary"].items():
            f.write(
                f"| {category} | {stats['spans']} | {stats['tokens']} | {stats['avg_tps']} |\n"
            )
        f.write("\n")
        f.write("Note: numeral spans can overlap categories (e.g., currency spans also contain digits).\n\n")

        f.write("## Conjunct Integrity (Halanta Cliffhangers)\n")
        f.write(f"- Total halanta markers: {conj_total}\n")
        f.write(f"- Tokens ending with halanta: {conj_fragmented}\n")
        f.write(f"- Integrity (1 - cliffhangers/total): {conj_integrity}\n\n")

        f.write("## Morphological Fragmentation (Postpositions)\n")
        f.write(f"- Words with suffix chain: {morph_total}\n")
        f.write(f"- Words with fragmented suffix: {morph_severed}\n")
        f.write(f"- Fragmentation rate: {morph_rate}\n\n")

        f.write("## Notes\n")
        f.write("- Suffix matching uses greedy longest-first stripping (max chain depth 6).\n")
        f.write("- Conjunct integrity flags tokens that end with a halanta as cliffhangers.\n")
        f.write("- Document ratios are computed only for full documents in the sample.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate nepalitokenizers WordPiece/SentencePiece on a sampled IRIIS subset."
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--split", default="train")
    parser.add_argument("--tokenizer", default=DEFAULT_TOKENIZER, choices=["wordpiece", "sentencepiece"])
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--target-words", type=int, default=40000)
    parser.add_argument("--max-docs", type=int, default=0)
    parser.add_argument("--text-col", default=None)
    parser.add_argument("--domain-col", default=None)
    parser.add_argument("--no-shuffle", action="store_false", dest="shuffle")
    parser.set_defaults(shuffle=True)

    args = parser.parse_args()

    result = evaluate_sample(args)
    write_csv_reports(result, args.output_dir)
    write_markdown_report(result, args.output_dir)

    print("Evaluation complete.")
    print(f"- Output directory: {args.output_dir}")
    print(f"- Words evaluated: {result['actual_words']}")


if __name__ == "__main__":
    main()
