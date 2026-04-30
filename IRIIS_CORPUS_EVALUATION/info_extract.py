"""
corpus_evaluation_report.py  —  LINGUA-NEP / IRIIS Corpus Evaluation
======================================================================
Performance rewrite: uses datasets.map() with batched=True + num_proc=N
instead of a single-threaded Python for-loop. On a 32-core machine with
5.2M rows this drops wall-time from ~3 hours to ~8-15 minutes.

Architecture
------------
  1. load_dataset()          — loads all Arrow shards into RAM in parallel
  2. ds.map(analyse_batch)   — per-batch stats across all N cores in parallel
  3. Reduce partial counters — sum aggregates returned from each batch
  4. Write Markdown report

Columns detected at runtime (IRIIS: 'index', 'Article', 'Source').
"""

import re
import os
import hashlib
import json
import collections
import multiprocessing
from urllib.parse import urlparse
import numpy as np

from datasets import load_dataset
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────────────────────
# Constants — module-level for clean multiprocessing pickling
# ─────────────────────────────────────────────────────────────────────────────

NEPALI_SUFFIXES = sorted(
    [
        "हरुलाई", "हरुबाट", "हरुसँग", "हरुको", "हरुका", "हरुकी", "हरुले", "हरुमा",
        "हरू", "हरु",
        "सँगै", "सँग", "भन्दा", "बाट", "लाई", "तिर",
        "मा", "ले", "को", "का", "की",
    ],
    key=len, reverse=True,
)

sentence_re = re.compile(r"[।\.!\?]+\s*|\n+")

SENTENCE_RE = re.compile(r"[।\.!\?]+\s*|\n+")
HTML_RE     = re.compile(r"<[^>]{1,200}?>")
URL_RE      = re.compile(r"https?://\S+|www\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}\S*")
PHONE_RE    = re.compile(
    r"\b(?:\+977[- .]?)?(?:98|97|96|01|0\d)[- .]?\d{7,8}\b|[०-९]{9,10}"
)
STRIP_CHARS = ".,?!\u0964\u0965'\"()[]{}:;-\u2013\u2014"

DEV_LO, DEV_HI         = 0x0900, 0x097F #devanagari word range bounds
DIG_LO, DIG_HI         = 0x0966, 0x096F #devanagari digits ०-९
HALANTA_CP              = 0x094D        #halanta (virama) char used in conjuncts
LAT_UP_LO, LAT_UP_HI   = 0x0041, 0x005A #a-zA-Z Latin chars
LAT_LO_LO, LAT_LO_HI   = 0x0061, 0x007A # lowercase a-z
ASC_DIG_LO, ASC_DIG_HI = 0x0030, 0x0039 # ASCII digits 0-9

EMOJI_RANGES = [
    (0x1F300,0x1F5FF),(0x1F600,0x1F64F),(0x1F650,0x1F67F),(0x1F680,0x1F6FF),
    (0x1F700,0x1F77F),(0x1F780,0x1F7FF),(0x1F800,0x1F8FF),(0x1F900,0x1F9FF),
    (0x1FA00,0x1FA6F),(0x1FA70,0x1FAFF),(0x2600,0x26FF),(0x2700,0x27BF),
    (0x231A,0x231B),(0x23E9,0x23F3),(0x25AA,0x25AB),(0x25B6,0x25B6),
    (0x25C0,0x25C0),(0x25FB,0x25FE),(0x2614,0x2615),(0x2648,0x2653),
    (0x2693,0x2693),(0x26A1,0x26A1),(0x26AA,0x26AB),(0x26BD,0x26BE),
    (0x26C4,0x26C5),(0x26D4,0x26D4),(0x26F2,0x26F3),(0x26F5,0x26F5),
    (0x26FA,0x26FA),(0x26FD,0x26FD),(0x2702,0x2702),(0x2705,0x2705),
    (0x2708,0x270D),(0x270F,0x270F),(0x2712,0x2712),(0x2714,0x2714),
    (0x2716,0x2716),(0x271D,0x271D),(0x2721,0x2721),(0x2728,0x2728),
    (0x2733,0x2734),(0x2744,0x2744),(0x2747,0x2747),(0x274C,0x274C),
    (0x274E,0x274E),(0x2753,0x2755),(0x2757,0x2757),(0x2763,0x2764),
    (0x2795,0x2797),(0x27A1,0x27A1),(0x27B0,0x27B0),(0x27BF,0x27BF),
    (0xFE00,0xFE0F),(0x1F1E0,0x1F1FF),
]

# returns True if cp lies inside EMOJI_RANGES defined above
def _is_emoji(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)

# dataset structure and column names 
TEXT_COL   = "Article"
DOMAIN_COL = "Source"

def analyse_batch(batch: dict) -> dict:
    total_docs = total_sentences = total_words = 0
    total_chars = total_bytes_ = 0
    dev_chars = lat_chars = dev_digits = asc_digits = halanta = emojis = 0
    html_c = url_c = phone_c = dup_c = suffix_bearing = 0

    word_freq   = collections.Counter()
    domain_freq = collections.Counter()
    suffix_freq = collections.Counter()
    doc_lens_s, doc_lens_w, sent_lens_w = [], [], []
    seen: set = set()

    texts   = batch[TEXT_COL]
    domains = batch.get(DOMAIN_COL, [None] * len(texts))

    for text, raw_domain in zip(texts, domains):
        if not text:
            continue
        text = str(text)

        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        if h in seen:
            dup_c += 1
            continue
        seen.add(h)

        total_docs += 1
        total_chars += len(text)
        total_bytes_ += len(text.encode("utf-8"))

        if raw_domain:
            p = urlparse(str(raw_domain))
            domain_freq[p.netloc or str(raw_domain)] += 1
        else:
            domain_freq["Unknown"] += 1

        html_c  += len(HTML_RE.findall(text))
        url_c   += len(URL_RE.findall(text))
        phone_c += len(PHONE_RE.findall(text))

        for ch in text:
            cp = ord(ch)
            if _is_emoji(cp):
                emojis += 1
            elif DEV_LO <= cp <= DEV_HI:
                dev_chars += 1
                if DIG_LO <= cp <= DIG_HI:
                    dev_digits += 1
                if cp == HALANTA_CP:
                    halanta += 1
            elif LAT_UP_LO <= cp <= LAT_UP_HI or LAT_LO_LO <= cp <= LAT_LO_HI:
                lat_chars += 1
            elif ASC_DIG_LO <= cp <= ASC_DIG_HI:
                asc_digits += 1

        sents = [s.strip() for s in SENTENCE_RE.split(text) if s.strip()] or [text]
        total_sentences += len(sents)
        doc_lens_s.append(len(sents))

        doc_wc = 0
        for sent in sents:
            words = sent.split()
            sent_lens_w.append(len(words))
            doc_wc += len(words)
            for word in words:
                wc = word.strip(STRIP_CHARS)
                if not wc:
                    continue
                word_freq[wc] += 1
                for suf in NEPALI_SUFFIXES:
                    if wc.endswith(suf) and len(wc) > len(suf):
                        suffix_freq[suf] += 1
                        suffix_bearing += 1
                        break

        doc_lens_w.append(doc_wc)
        total_words += doc_wc

    return {
        "_n":          [total_docs],
        "_sents":      [total_sentences],
        "_words":      [total_words],
        "_chars":      [total_chars],
        "_bytes":      [total_bytes_],
        "_dev":        [dev_chars],
        "_lat":        [lat_chars],
        "_ddev":       [dev_digits],
        "_dasc":       [asc_digits],
        "_hal":        [halanta],
        "_emo":        [emojis],
        "_html":       [html_c],
        "_url":        [url_c],
        "_phone":      [phone_c],
        "_dup":        [dup_c],
        "_sufb":       [suffix_bearing],
        # JSON strings — avoids Arrow schema mismatch across batches
        "_wfreq":      [json.dumps(dict(word_freq.most_common(50_000)), ensure_ascii=False)],
        "_dfreq":      [json.dumps(dict(domain_freq), ensure_ascii=False)],
        "_sfreq":      [json.dumps(dict(suffix_freq), ensure_ascii=False)],
        "_dls":        [json.dumps(doc_lens_s)],
        "_dlw":        [json.dumps(doc_lens_w)],
        "_slw":        [json.dumps(sent_lens_w)],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Stats helper
# ─────────────────────────────────────────────────────────────────────────────

def get_stats(data: list) -> dict:
    if not data:
        return {"min":0,"q1":0,"median":0,"q3":0,"max":0,"mean":0.0}
    s = np.array(sorted(data))
    n = len(s)

    q1, median, q3 = np.percentile(s, [25, 50, 75])

    return {
        "min": int(s[0]),
        "q1": float(round(float(q1), 2)),
        "median": float(round(float(median), 2)),
        "q3": float(round(float(q3), 2)),
        "max": int(s[-1]),
        "mean": round(sum(data)/n, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Report generator
# ─────────────────────────────────────────────────────────────────────────────

def _print_report_header(ds, n_proc, batch_size):
    """Print a short runtime header showing dataset and worker settings.

    Args:
        ds: HuggingFace Dataset object.
        n_proc: Number of worker processes used for mapping.
        batch_size: Number of rows per batch passed to the mapper.
    """
    print(f"  Columns      : {ds.column_names}")
    print(f"  Text column  : '{TEXT_COL}'")
    print(f"  Domain col   : '{DOMAIN_COL}'")
    print(f"  Workers      : {n_proc}  |  Batch size: {batch_size}")
    print(f"  Total rows   : {len(ds):,}\n")


def _run_map(ds, n_proc, batch_size):
    """Run `ds.map()` with `analyse_batch` in parallel and return the result.

    Important options:
    - `batched=True` so the mapper receives lists (batches) instead of single rows.
    - `remove_columns` drops original text columns from the returned Dataset to keep
      the per-batch result compact.
    """
    print("Running parallel map()...")
    return ds.map(
        analyse_batch,
        batched=True,
        batch_size=batch_size,
        num_proc=n_proc,
        remove_columns=ds.column_names,
        desc="Analysing",
    )


def _reduce_results(res):
    """Aggregate per-batch results in `res` into corpus-level statistics.

    Returns a tuple: (stats_dict, word_counter, domain_counter, suffix_counter,
    doc_sent_stats, doc_word_stats, sent_word_stats)
    """
    print("Reducing...")

    # Sum scalar counters across batches (each res["_..."] is a list of per-batch values)
    stats = {}
    stats["total_docs"] = sum(res["_n"])
    stats["total_sents"] = sum(res["_sents"])
    stats["total_words"] = sum(res["_words"])
    stats["total_chars"] = sum(res["_chars"])
    stats["total_bytes"] = sum(res["_bytes"])
    stats["dev_chars"] = sum(res["_dev"])
    stats["lat_chars"] = sum(res["_lat"])
    stats["dev_digits"] = sum(res["_ddev"])
    stats["asc_digits"] = sum(res["_dasc"])
    stats["halanta"] = sum(res["_hal"])
    stats["emojis"] = sum(res["_emo"])
    stats["html_c"] = sum(res["_html"])
    stats["url_c"] = sum(res["_url"])
    stats["phone_c"] = sum(res["_phone"])
    stats["dups"] = sum(res["_dup"])
    stats["sufb"] = sum(res["_sufb"])

    # Initialize accumulators for counters and distributions
    wfreq = collections.Counter()
    dfreq = collections.Counter()
    sfreq = collections.Counter()
    dls, dlw, slw = [], [], []

    # Merge JSON-serialized counters returned by each batch into global counters/lists
    for i in tqdm(range(len(res)), desc="Merging counters"):
        row = res[i]
        # `_wfreq` / `_dfreq` / `_sfreq` are JSON strings mapping item->count
        wfreq.update(json.loads(row["_wfreq"]))
        dfreq.update(json.loads(row["_dfreq"]))
        sfreq.update(json.loads(row["_sfreq"]))
        # `_dls`, `_dlw`, `_slw` are JSON lists of lengths — extend the master lists
        dls.extend(json.loads(row["_dls"]))
        dlw.extend(json.loads(row["_dlw"]))
        slw.extend(json.loads(row["_slw"]))

    # Derived statistics
    stats["unique"] = len(wfreq)
    stats["ttr"] = stats["unique"] / max(stats["total_words"], 1)
    stats["hapax"] = sum(1 for c in wfreq.values() if c == 1)
    stats["dup_rate"] = stats["dups"] / max(stats["total_docs"] + stats["dups"], 1)
    stats["ts"] = stats["dev_chars"] + stats["lat_chars"]
    stats["td"] = stats["dev_digits"] + stats["asc_digits"]

    # Compute distribution summaries for document/sentence lengths
    DS = get_stats(dls); DW = get_stats(dlw); SW = get_stats(slw)

    return stats, wfreq, dfreq, sfreq, DS, DW, SW


def _write_report(output_file, stats, wfreq, dfreq, sfreq, DS, DW, SW):
    print(f"\nWriting report → {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        W = f.write
        W("# Nepali Corpus Evaluation Report\n")
        W("*LINGUA-NEP / IRIIS-RESEARCH/Nepali-Text-Corpus*\n\n")

        W("## 1. Corpus Size Metrics\n")
        W(f"- **Total Documents (post-dedup):** {stats['total_docs']:,}\n")
        W(f"- **Exact Duplicates Removed:** {stats['dups']:,}  ({stats['dup_rate']:.2%})\n")
        W(f"- **Total Sentences:** {stats['total_sents']:,}\n")
        W(f"- **Total Words (tokens):** {stats['total_words']:,}\n")
        W(f"- **Total Characters:** {stats['total_chars']:,}\n")
        W(f"- **Total Bytes (UTF-8):** {stats['total_bytes']:,} (≈ {stats['total_bytes']/(1024**3):.2f} GB)\n\n")

        W("## 2. Vocabulary & Typology\n")
        W(f"- **Unique Word Types:** {stats['unique']:,}\n")
        W(f"- **Type-Token Ratio (TTR):** {stats['ttr']:.5f}\n")
        W(f"- **Hapax Legomena:** {stats['hapax']:,}\n")
        W(f"- **Hapax / Total Tokens:** {stats['hapax']/max(stats['total_words'],1):.5f}\n")
        W(f"- **Hapax / Unique Types:** {stats['hapax']/max(stats['unique'],1):.5f}\n\n")

        W("## 3. Source / Domain Distribution\n")
        for dom, cnt in dfreq.most_common(15):
            W(f"- **{dom}**: {cnt:,}\n")
        W("\n")

        W("## 4. Length Distributions\n")
        W("### Document Lengths (sentences)\n")
        W(f"- Mean: {DS['mean']} | Median: {DS['median']} | Q1: {DS['q1']} | Q3: {DS['q3']} | Max: {DS['max']}\n")
        W("### Document Lengths (words)\n")
        W(f"- Mean: {DW['mean']} | Median: {DW['median']} | Q1: {DW['q1']} | Q3: {DW['q3']} | Max: {DW['max']}\n")
        W("### Sentence Lengths (words)\n")
        W(f"- Mean: {SW['mean']} | Median: {SW['median']} | Q1: {SW['q1']} | Q3: {SW['q3']} | Max: {SW['max']}\n\n")

        W("## 5. Devanagari vs Latin Script Ratio\n")
        W(f"- **Devanagari Characters:** {stats['dev_chars']:,}\n")
        W(f"- **Latin Characters:** {stats['lat_chars']:,}\n")
        if stats['ts']: W(f"- **Ratio:** {stats['dev_chars']/stats['ts']:.2%} Devanagari / {stats['lat_chars']/stats['ts']:.2%} Latin\n")
        W(f"- **Other (punct, space, symbols):** {stats['total_chars']-stats['dev_chars']-stats['lat_chars']-stats['asc_digits']:,}\n\n")

        W("## 6. Digit Distribution (Devanagari vs ASCII)\n")
        W(f"- **Devanagari Digits (०–९):** {stats['dev_digits']:,}\n")
        W(f"- **ASCII Digits (0–9):** {stats['asc_digits']:,}\n")
        if stats['td']: W(f"- **Ratio:** {stats['dev_digits']/stats['td']:.2%} Devanagari / {stats['asc_digits']/stats['td']:.2%} ASCII\n")
        W("\n  > **LinguaBPE H3:** High Devanagari-digit ratio justifies numeral normalisation layer.\n\n")

        W("## 7. Halanta & Conjuncts\n")
        W(f"- **Halanta (् U+094D) Count:** {stats['halanta']:,}\n")
        if stats['dev_chars']: W(f"- **Halanta Density:** {stats['halanta']/stats['dev_chars']:.4%} of all Devanagari chars\n")
        W("  > **LinguaBPE H2:** Each Halanta = one conjunct vulnerable to byte-level fragmentation.\n\n")

        W("## 8. Suffix-bearing Words\n")
        W(f"- **Suffix-bearing Words:** {stats['sufb']:,} ({stats['sufb']/max(stats['total_words'],1):.2%} of total)\n")
        W("  > Longest-first matching: हरुको counted as हरुको, not को.\n")
        W("- **Per-suffix counts:**\n")
        for suf, cnt in sfreq.most_common(20):
            W(f"  - `{suf}`: {cnt:,}  ({cnt/max(stats['sufb'],1):.2%})\n")
        W("\n")

        W("## 9. Noise Rates\n")
        W(f"- **HTML Remnants:** {stats['html_c']:,}\n")
        W(f"- **URLs:** {stats['url_c']:,}\n")
        W(f"- **Phone Numbers:** {stats['phone_c']:,}\n")
        W(f"- **Emojis:** {stats['emojis']:,}\n\n")

        W("## 10. Top 50 Most Frequent Words\n")
        for word, cnt in wfreq.most_common(50):
            W(f"- `{word}`: {cnt:,}\n")

    print(f"\n✅ Report saved → {output_file}")


def generate_report(ds, output_file="corpus_evaluation_report_corrected.md",
                    n_proc=None, batch_size=2000):
    global TEXT_COL, DOMAIN_COL

    n_proc = n_proc or multiprocessing.cpu_count()

    _print_report_header(ds, n_proc, batch_size)

    res = _run_map(ds, n_proc, batch_size)

    stats, wfreq, dfreq, sfreq, DS, DW, SW = _reduce_results(res)

    _write_report(output_file, stats, wfreq, dfreq, sfreq, DS, DW, SW)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    n_cores = multiprocessing.cpu_count() # count the available CPU cores for parallel processing
    print(f"Cores: {n_cores}  |  Loading IRIIS corpus into RAM...")

    ds = load_dataset(
        "IRIIS-RESEARCH/Nepali-Text-Corpus",
        split="train",
        num_proc=n_cores, # used for enabling multiprocessing. 
    )

    print(f"Loaded: {len(ds):,} rows | {ds.column_names}\n")

    base_dir = os.path.dirname(os.path.abspath(__file__)) # __file__ is the current script path
    report_path = os.path.join(base_dir, "corpus_evaluation_reportt.md")

    generate_report(ds, output_file=report_path, n_proc=n_cores, batch_size=2000)