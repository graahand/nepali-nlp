"""
corpus_evaluation_report.py  —  LINGUA-NEP / IRIIS Corpus Evaluation
======================================================================
Corrected version. Fixes vs original:

  BUG-1  Latin/ASCII digit counts were 0 because character scanning
         happened only inside word_clean; now scanned on raw `text` directly.

  BUG-2  Sentence splitter missed Nepali । (Purna Viram) when not followed
         by a space; now also splits on ।\n and bare newlines.

  BUG-3  hash(text) is non-deterministic (Python hash randomisation); replaced
         with hashlib.md5 for reproducible deduplication.

  BUG-4  Source/domain field: IRIIS corpus has no "url" or "source" column;
         code now inspects all available keys and picks the best candidate.

  BUG-5  Suffix matching was not longest-first; short suffixes (को) were
         absorbing words that should have matched हरुको or लाई first.

  BUG-6  Emoji detection via unicodedata.category == 'So' misses the vast
         majority of modern emoji (U+1F300+); replaced with a Unicode range
         check that covers all current emoji blocks.
"""

import re
import hashlib
import collections
import unicodedata
from urllib.parse import urlparse

from datasets import load_dataset
from tqdm import tqdm


# ── Nepali suffixes — longest first so greedy match is correct ────────────────
NEPALI_SUFFIXES = sorted(
    [
        # Multi-character agglutinative chains
        "हरुलाई", "हरुबाट", "हरुसँग", "हरुको", "हरुका", "हरुकी", "हरुले", "हरुमा",
        "हरू",    "हरु",
        # Vibhakti (case markers)
        "सँगै", "सँग",
        "भन्दा",
        "बाट",
        "लाई",
        "तिर",
        "मा",
        "ले",
        "को", "का", "की",
    ],
    key=len,
    reverse=True,   # longest suffix matched first
)

# Sentence boundary pattern — handles ।, .  !  ?  and bare newlines
SENTENCE_RE = re.compile(r"[।\.\!\?]+[\s]*|[\n]+")

# Devanagari Unicode block: U+0900–U+097F
DEVANAGARI_BLOCK = (0x0900, 0x097F)
# Devanagari digit range: U+0966–U+096F  (०–९)
DEV_DIGIT_RANGE  = (0x0966, 0x096F)
# Halanta (virama): U+094D  (्)
HALANTA_CP = 0x094D

# Basic Latin letters
LATIN_UPPER = (0x0041, 0x005A)  # A–Z
LATIN_LOWER = (0x0061, 0x007A)  # a–z
# ASCII digits
ASCII_DIGIT = (0x0030, 0x0039)  # 0–9

# Emoji Unicode ranges (BUG-6 fix: comprehensive list)
EMOJI_RANGES = [
    (0x1F300, 0x1F5FF),   # Misc symbols & pictographs
    (0x1F600, 0x1F64F),   # Emoticons
    (0x1F650, 0x1F67F),   # Ornamental dingbats
    (0x1F680, 0x1F6FF),   # Transport & map
    (0x1F700, 0x1F77F),   # Alchemical symbols
    (0x1F780, 0x1F7FF),   # Geometric shapes extended
    (0x1F800, 0x1F8FF),   # Supplemental arrows
    (0x1F900, 0x1F9FF),   # Supplemental symbols
    (0x1FA00, 0x1FA6F),   # Chess symbols
    (0x1FA70, 0x1FAFF),   # Symbols and pictographs extended-A
    (0x2600,  0x26FF),    # Misc symbols
    (0x2700,  0x27BF),    # Dingbats
    (0x231A,  0x231B),    # Watch, hourglass
    (0x23E9,  0x23F3),    # Various clock/timer symbols
    (0x25AA,  0x25AB),    # Small squares
    (0x25B6,  0x25B6),    # Play button
    (0x25C0,  0x25C0),    # Reverse button
    (0x25FB,  0x25FE),    # Medium squares
    (0x2614,  0x2615),    # Umbrella/hot beverage
    (0x2648,  0x2653),    # Zodiac signs
    (0x267F,  0x267F),    # Wheelchair symbol
    (0x2693,  0x2693),    # Anchor
    (0x26A1,  0x26A1),    # Lightning
    (0x26AA,  0x26AB),    # Circles
    (0x26BD,  0x26BE),    # Soccer/baseball
    (0x26C4,  0x26C5),    # Snowman/sun
    (0x26CE,  0x26CE),    # Ophiuchus
    (0x26D4,  0x26D4),    # No entry
    (0x26EA,  0x26EA),    # Church
    (0x26F2,  0x26F3),    # Fountain/golf
    (0x26F5,  0x26F5),    # Sailboat
    (0x26FA,  0x26FA),    # Tent
    (0x26FD,  0x26FD),    # Fuel pump
    (0x2702,  0x2702),    # Scissors
    (0x2705,  0x2705),    # Check mark
    (0x2708,  0x270D),    # Airplane–writing hand
    (0x270F,  0x270F),    # Pencil
    (0x2712,  0x2712),    # Black nib
    (0x2714,  0x2714),    # Heavy check
    (0x2716,  0x2716),    # Heavy multiplication
    (0x271D,  0x271D),    # Latin cross
    (0x2721,  0x2721),    # Star of David
    (0x2728,  0x2728),    # Sparkles
    (0x2733,  0x2734),    # Asterisks
    (0x2744,  0x2744),    # Snowflake
    (0x2747,  0x2747),    # Sparkle
    (0x274C,  0x274C),    # Cross mark
    (0x274E,  0x274E),    # Cross mark button
    (0x2753,  0x2755),    # Question marks
    (0x2757,  0x2757),    # Exclamation mark
    (0x2763,  0x2764),    # Heart exclamation, heart
    (0x2795,  0x2797),    # Plus, minus, division
    (0x27A1,  0x27A1),    # Arrow
    (0x27B0,  0x27B0),    # Curly loop
    (0x27BF,  0x27BF),    # Double curly loop
    (0xFE00,  0xFE0F),    # Variation selectors (emoji modifiers)
    (0x1F1E0, 0x1F1FF),   # Regional indicator letters (flag sequences)
]


def is_emoji(cp: int) -> bool:
    """BUG-6 FIX: Check if a code-point falls in any known emoji range."""
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)


def stable_hash(text: str) -> str:
    """BUG-3 FIX: Use MD5 instead of Python's non-deterministic hash()."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_stats(data: list) -> dict:
    if not data:
        return {"min": 0, "q1": 0, "median": 0, "q3": 0, "max": 0, "mean": 0.0}
    s = sorted(data)
    n = len(s)
    return {
        "min":    s[0],
        "q1":     s[n // 4],
        "median": s[n // 2],
        "q3":     s[3 * n // 4],
        "max":    s[-1],
        "mean":   round(sum(data) / n, 2),
    }


def detect_text_column(first_doc: dict) -> str:
    """
    BUG-4 FIX: Robustly detect the text column from available keys.
    IRIIS corpus may not have 'url' or 'source' fields.
    """
    keys = list(first_doc.keys())
    print(f"  Available columns: {keys}")
    lower = {k.lower(): k for k in keys}

    # Priority order for text column
    for candidate in ["text", "content", "article", "body", "paragraph", "sentence"]:
        if candidate in lower:
            return lower[candidate]

    # Fall back to the first non-id-like string column
    for k in keys:
        v = first_doc[k]
        if isinstance(v, str) and k.lower() not in {"id", "index", "url", "source", "domain"}:
            return k

    return keys[0]


def detect_domain_column(first_doc: dict) -> str | None:
    """
    BUG-4 FIX: Detect domain/source column. Returns None if absent.
    """
    keys = list(first_doc.keys())
    lower = {k.lower(): k for k in keys}
    for candidate in ["url", "domain", "source", "website", "origin", "site"]:
        if candidate in lower:
            return lower[candidate]
    return None


def generate_report(ds, output_file: str = "corpus_evaluation_report.md"):
    # ── Counters & accumulators ───────────────────────────────────────────────
    total_docs = 0
    total_sentences = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0

    word_freq: collections.Counter = collections.Counter()
    domain_dist: collections.Counter = collections.Counter()

    doc_lengths_sentences: list[int] = []
    doc_lengths_words: list[int] = []
    sent_lengths_words: list[int] = []

    # BUG-1 FIX: count chars directly on raw text, not on word_clean
    devanagari_chars = 0
    latin_chars = 0
    devanagari_digits = 0
    ascii_digits = 0
    halanta_count = 0

    suffix_dist: collections.Counter = collections.Counter()
    suffix_bearing_words = 0

    seen_hashes: set[str] = set()   # BUG-3 FIX: MD5 hashes
    duplicate_docs = 0

    html_tags_count = 0
    urls_count = 0
    phone_numbers_count = 0
    emojis_count = 0

    # Regex patterns
    html_pattern   = re.compile(r"<[^>]{1,200}?>")
    url_pattern    = re.compile(
        r"https?://[^\s]+"                       # explicit https/http
        r"|www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*"  # www. bare domains
    )
    phone_pattern  = re.compile(
        r"\b(?:\+977[- .]?)?(?:98|97|96|01|0\d)[- .]?\d{7,8}\b"  # ASCII digits
        r"|[०-९]{9,10}"                                             # Devanagari digits
    )

    # ── Detect columns from first document ───────────────────────────────────
    print("Analysing corpus...")
    first_doc = ds[0] if hasattr(ds, "__getitem__") else next(iter(ds))
    text_col   = detect_text_column(first_doc)
    domain_col = detect_domain_column(first_doc)

    # len() works on an in-memory Dataset; undefined on a streaming IterableDataset
    total_rows = len(ds) if hasattr(ds, "__len__") else None
    if total_rows:
        print(f"  Total rows    : {total_rows:,}\n")
    print(f"  Text column   : '{text_col}'")
    print(f"  Domain column : '{domain_col}' (None = will mark Unknown)")

    # ── Main loop ─────────────────────────────────────────────────────────────
    for doc in tqdm(ds, desc="Processing", total=total_rows):
        text = str(doc.get(text_col, ""))
        if not text:
            continue

        # BUG-3 FIX: deterministic dedup
        doc_hash = stable_hash(text)
        if doc_hash in seen_hashes:
            duplicate_docs += 1
            continue
        seen_hashes.add(doc_hash)

        total_docs += 1
        total_chars += len(text)
        total_bytes += len(text.encode("utf-8"))

        # BUG-4 FIX: domain extraction
        if domain_col:
            raw_domain = doc.get(domain_col, "")
            if raw_domain:
                parsed = urlparse(str(raw_domain))
                domain = parsed.netloc or str(raw_domain)
            else:
                domain = "Unknown"
        else:
            domain = "Unknown"
        domain_dist[domain] += 1

        # Noise detection (on raw text)
        html_tags_count       += len(html_pattern.findall(text))
        urls_count            += len(url_pattern.findall(text))
        phone_numbers_count   += len(phone_pattern.findall(text))

        # BUG-1 FIX: character counting on raw text
        for char in text:
            cp = ord(char)
            # BUG-6 FIX: emoji via range check
            if is_emoji(cp):
                emojis_count += 1
            elif DEVANAGARI_BLOCK[0] <= cp <= DEVANAGARI_BLOCK[1]:
                devanagari_chars += 1
                if DEV_DIGIT_RANGE[0] <= cp <= DEV_DIGIT_RANGE[1]:
                    devanagari_digits += 1
                if cp == HALANTA_CP:
                    halanta_count += 1
            elif LATIN_UPPER[0] <= cp <= LATIN_UPPER[1] or LATIN_LOWER[0] <= cp <= LATIN_LOWER[1]:
                latin_chars += 1
            elif ASCII_DIGIT[0] <= cp <= ASCII_DIGIT[1]:
                ascii_digits += 1

        # BUG-2 FIX: sentence splitting — also split on ।\n and bare newlines
        sentences = [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]
        if not sentences:
            sentences = [text]
        total_sentences     += len(sentences)
        doc_lengths_sentences.append(len(sentences))

        doc_word_count = 0
        for sent in sentences:
            words = sent.split()
            sent_lengths_words.append(len(words))
            doc_word_count += len(words)

            for word in words:
                word_clean = word.strip(".,?!।'\u0964\u0965\"()[]{}:;-–—")
                if not word_clean:
                    continue
                word_freq[word_clean] += 1

                # BUG-5 FIX: suffix matching — longest first, already sorted
                for suffix in NEPALI_SUFFIXES:
                    if word_clean.endswith(suffix) and len(word_clean) > len(suffix):
                        suffix_dist[suffix] += 1
                        suffix_bearing_words += 1
                        break  # only count once per word (first/longest match)

        doc_lengths_words.append(doc_word_count)
        total_words += doc_word_count

    # ── Aggregate statistics ──────────────────────────────────────────────────
    unique_words    = len(word_freq)
    ttr             = unique_words / max(total_words, 1)
    hapax_legomena  = sum(1 for c in word_freq.values() if c == 1)
    hapax_ratio_tokens = hapax_legomena / max(total_words, 1)    # per proposal convention
    hapax_ratio_types  = hapax_legomena / max(unique_words, 1)   # also report this

    duplicate_rate  = duplicate_docs / max(total_docs + duplicate_docs, 1)

    total_script_chars = devanagari_chars + latin_chars
    total_digit_chars  = devanagari_digits + ascii_digits

    doc_len_sent_stats = get_stats(doc_lengths_sentences)
    doc_len_word_stats = get_stats(doc_lengths_words)
    sent_len_word_stats = get_stats(sent_lengths_words)

    # ── Write Markdown report ─────────────────────────────────────────────────
    print(f"\nWriting report → {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:

        f.write("# Nepali Corpus Evaluation Report\n")
        f.write("*LINGUA-NEP / IRIIS-RESEARCH/Nepali-Text-Corpus*\n\n")

        # §1 Corpus size
        f.write("## 1. Corpus Size Metrics\n")
        f.write(f"- **Total Documents (after dedup):** {total_docs:,}\n")
        f.write(f"- **Total Sentences:** {total_sentences:,}\n")
        f.write(f"- **Total Words (tokens):** {total_words:,}\n")
        f.write(f"- **Total Characters:** {total_chars:,}\n")
        f.write(f"- **Total Bytes (UTF-8):** {total_bytes:,} "
                f"(≈ {total_bytes / (1024**3):.2f} GB)\n\n")

        # §2 Vocabulary
        f.write("## 2. Vocabulary & Typology\n")
        f.write(f"- **Unique Word Types:** {unique_words:,}\n")
        f.write(f"- **Type-Token Ratio (TTR):** {ttr:.5f}\n")
        f.write(f"- **Hapax Legomena:** {hapax_legomena:,}\n")
        f.write(f"- **Hapax / Total Tokens:** {hapax_ratio_tokens:.5f}\n")
        f.write(f"- **Hapax / Unique Types:** {hapax_ratio_types:.5f}  "
                f"*(fraction of vocabulary appearing only once)*\n\n")

        # §3 Source/domain
        f.write("## 3. Source / Domain Distribution\n")
        for domain, count in domain_dist.most_common(15):
            f.write(f"- **{domain}**: {count:,} documents\n")
        f.write("\n")

        # §4 Length distributions
        f.write("## 4. Length Distributions\n")
        f.write("### Document Lengths (sentences)\n")
        f.write(f"- Mean: {doc_len_sent_stats['mean']:.2f}  |  "
                f"Median: {doc_len_sent_stats['median']}  |  "
                f"Q1: {doc_len_sent_stats['q1']}  |  "
                f"Q3: {doc_len_sent_stats['q3']}  |  "
                f"Max: {doc_len_sent_stats['max']}\n")
        f.write("### Document Lengths (words)\n")
        f.write(f"- Mean: {doc_len_word_stats['mean']:.2f}  |  "
                f"Median: {doc_len_word_stats['median']}  |  "
                f"Q1: {doc_len_word_stats['q1']}  |  "
                f"Q3: {doc_len_word_stats['q3']}  |  "
                f"Max: {doc_len_word_stats['max']}\n")
        f.write("### Sentence Lengths (words)\n")
        f.write(f"- Mean: {sent_len_word_stats['mean']:.2f}  |  "
                f"Median: {sent_len_word_stats['median']}  |  "
                f"Q1: {sent_len_word_stats['q1']}  |  "
                f"Q3: {sent_len_word_stats['q3']}  |  "
                f"Max: {sent_len_word_stats['max']}\n\n")

        # §5 Script ratio
        f.write("## 5. Devanagari vs Latin Script Ratio\n")
        f.write(f"- **Devanagari Characters:** {devanagari_chars:,}\n")
        f.write(f"- **Latin Characters:** {latin_chars:,}\n")
        if total_script_chars > 0:
            f.write(f"- **Ratio:** {devanagari_chars / total_script_chars:.2%} Devanagari  /  "
                    f"{latin_chars / total_script_chars:.2%} Latin\n")
        f.write(f"- **Other Characters (punct, spaces, etc.):** "
                f"{total_chars - devanagari_chars - latin_chars - ascii_digits:,}\n\n")

        # §6 Digit distribution
        f.write("## 6. Digit Distribution (Devanagari vs ASCII)\n")
        f.write(f"- **Devanagari Digits (०–९):** {devanagari_digits:,}\n")
        f.write(f"- **ASCII Digits (0–9):** {ascii_digits:,}\n")
        if total_digit_chars > 0:
            f.write(f"- **Ratio:** {devanagari_digits / total_digit_chars:.2%} Devanagari  /  "
                    f"{ascii_digits / total_digit_chars:.2%} ASCII\n")
        f.write("\n  > **Note for LinguaBPE:** The Devanagari/ASCII split directly motivates "
                "the numeral-normalisation layer (Hypothesis H3). A high Devanagari-digit ratio "
                "means the normalisation will have broad coverage.\n\n")

        # §7 Halanta
        f.write("## 7. Halanta & Conjuncts\n")
        f.write(f"- **Halanta (्  U+094D) Count:** {halanta_count:,}\n")
        if devanagari_chars > 0:
            f.write(f"- **Halanta Density:** {halanta_count / devanagari_chars:.4%} "
                    f"of all Devanagari chars\n")
        f.write("  > Halanta count is the primary empirical evidence for Hypothesis H2 "
                "(conjunct preservation). Each Halanta instance represents a conjunct that "
                "standard BPE may fragment.\n\n")

        # §8 Suffix-bearing words
        f.write("## 8. Suffix-bearing Words\n")
        f.write(f"- **Suffix-bearing Words:** {suffix_bearing_words:,} "
                f"({suffix_bearing_words / max(total_words, 1):.2%} of total words)\n")
        f.write("  > Longest-first matching ensures हरुको is not mis-counted as को.\n")
        f.write("- **Top Suffix Occurrences:**\n")
        for suffix, count in suffix_dist.most_common(15):
            f.write(f"  - `{suffix}`: {count:,}  "
                    f"({count / max(suffix_bearing_words, 1):.2%} of suffix-bearing words)\n")
        f.write("\n")

        # §9 Duplication
        f.write("## 9. Formatting & Duplication\n")
        f.write(f"- **Exact Duplicate Documents:** {duplicate_docs:,}\n")
        f.write(f"- **Exact Duplicate Rate:** {duplicate_rate:.2%}\n")
        f.write("  > Near-duplicate detection (e.g. same article with minor edits) "
                "requires MinHash or SimHash — not implemented here.\n\n")

        # §10 Noise
        f.write("## 10. Noise Rates\n")
        f.write(f"- **HTML Element Remnants:** {html_tags_count:,}\n")
        f.write(f"- **URLs Found:** {urls_count:,}  *(https:// + www. bare domains)*\n")
        f.write(f"- **Phone Numbers Detected:** {phone_numbers_count:,}  "
                f"*(ASCII + Devanagari digit patterns)*\n")
        f.write(f"- **Emojis Found:** {emojis_count:,}  "
                f"*(comprehensive Unicode emoji block scan)*\n\n")

        # §11 Top vocabulary
        f.write("## 11. Top 30 Most Frequent Words\n")
        for word, count in word_freq.most_common(30):
            f.write(f"- `{word}`: {count:,}\n")
        f.write("\n")

    print(f"Done. Report saved → {output_file}")


if __name__ == "__main__":
    import os
    import multiprocessing

    n_cores = multiprocessing.cpu_count()
    print(f"Loading full dataset into RAM  (cores available: {n_cores})")
    print("This will use ~20–28 GB RAM and take 3–8 minutes to download/cache.\n")

    dataset = load_dataset(
        "IRIIS-RESEARCH/Nepali-Text-Corpus",
        split="train",
        trust_remote_code=True,
        num_proc=n_cores,       # parallel Arrow shard loading — saturates disk I/O
    )

    print(f"Dataset loaded: {len(dataset):,} rows  |  "
          f"columns: {dataset.column_names}\n")

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "corpus_evaluation_report_corrected.md",
    )
    generate_report(dataset, output_file=output_path)