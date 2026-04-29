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

SENTENCE_RE = re.compile(r"[।\.!\?]+\s*|\n+")
HTML_RE     = re.compile(r"<[^>]{1,200}?>")
URL_RE      = re.compile(r"https?://\S+|www\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}\S*")
PHONE_RE    = re.compile(
    r"\b(?:\+977[- .]?)?(?:98|97|96|01|0\d)[- .]?\d{7,8}\b|[०-९]{9,10}"
)
STRIP_CHARS = ".,?!\u0964\u0965'\"()[]{}:;-\u2013\u2014"

DEV_LO, DEV_HI         = 0x0900, 0x097F
DIG_LO, DIG_HI         = 0x0966, 0x096F
HALANTA_CP              = 0x094D
LAT_UP_LO, LAT_UP_HI   = 0x0041, 0x005A
LAT_LO_LO, LAT_LO_HI   = 0x0061, 0x007A
ASC_DIG_LO, ASC_DIG_HI = 0x0030, 0x0039

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

def _is_emoji(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)


# ─────────────────────────────────────────────────────────────────────────────
# Column detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_text_column(columns: list) -> str:
    lower = {c.lower(): c for c in columns}
    for cand in ["text", "content", "article", "body", "paragraph", "sentence"]:
        if cand in lower:
            return lower[cand]
    for c in columns:
        if c.lower() not in {"id", "index", "url", "source", "domain"}:
            return c
    return columns[0]

def detect_domain_column(columns: list):
    lower = {c.lower(): c for c in columns}
    for cand in ["url", "domain", "source", "website", "origin", "site"]:
        if cand in lower:
            return lower[cand]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Batch worker — called by datasets.map() in each subprocess
# ─────────────────────────────────────────────────────────────────────────────
# TEXT_COL / DOMAIN_COL are set as module globals before map() is called
# (avoids lambda / closure pickling issues on some platforms)

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
    s = sorted(data); n = len(s)
    return {"min":s[0],"q1":s[n//4],"median":s[n//2],"q3":s[3*n//4],
            "max":s[-1],"mean":round(sum(data)/n,2)}


# ─────────────────────────────────────────────────────────────────────────────
# Report generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(ds, output_file="corpus_evaluation_report_corrected.md",
                    n_proc=None, batch_size=2000):
    global TEXT_COL, DOMAIN_COL

    n_proc = n_proc or multiprocessing.cpu_count()
    TEXT_COL   = detect_text_column(ds.column_names)
    DOMAIN_COL = detect_domain_column(ds.column_names)

    print(f"  Columns      : {ds.column_names}")
    print(f"  Text column  : '{TEXT_COL}'")
    print(f"  Domain col   : '{DOMAIN_COL}'")
    print(f"  Workers      : {n_proc}  |  Batch size: {batch_size}")
    print(f"  Total rows   : {len(ds):,}\n")

    print("Running parallel map()...")
    res = ds.map(
        analyse_batch,
        batched=True,
        batch_size=batch_size,
        num_proc=n_proc,
        remove_columns=ds.column_names,
        desc="Analysing",
    )

    print("Reducing...")
    total_docs = sum(res["_n"])
    total_sents= sum(res["_sents"])
    total_words= sum(res["_words"])
    total_chars= sum(res["_chars"])
    total_bytes= sum(res["_bytes"])
    dev_chars  = sum(res["_dev"])
    lat_chars  = sum(res["_lat"])
    dev_digits = sum(res["_ddev"])
    asc_digits = sum(res["_dasc"])
    halanta    = sum(res["_hal"])
    emojis     = sum(res["_emo"])
    html_c     = sum(res["_html"])
    url_c      = sum(res["_url"])
    phone_c    = sum(res["_phone"])
    dups       = sum(res["_dup"])
    sufb       = sum(res["_sufb"])

    wfreq = collections.Counter()
    dfreq = collections.Counter()
    sfreq = collections.Counter()
    dls, dlw, slw = [], [], []

    for i in tqdm(range(len(res)), desc="Merging counters"):
        row = res[i]
        wfreq.update(json.loads(row["_wfreq"]))
        dfreq.update(json.loads(row["_dfreq"]))
        sfreq.update(json.loads(row["_sfreq"]))
        dls.extend(json.loads(row["_dls"]))
        dlw.extend(json.loads(row["_dlw"]))
        slw.extend(json.loads(row["_slw"]))

    unique  = len(wfreq)
    ttr     = unique / max(total_words, 1)
    hapax   = sum(1 for c in wfreq.values() if c == 1)
    dup_rate= dups / max(total_docs + dups, 1)
    ts      = dev_chars + lat_chars
    td      = dev_digits + asc_digits

    DS = get_stats(dls); DW = get_stats(dlw); SW = get_stats(slw)

    print(f"\nWriting report → {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        W = f.write
        W("# Nepali Corpus Evaluation Report\n")
        W("*LINGUA-NEP / IRIIS-RESEARCH/Nepali-Text-Corpus*\n\n")

        W("## 1. Corpus Size Metrics\n")
        W(f"- **Total Documents (post-dedup):** {total_docs:,}\n")
        W(f"- **Exact Duplicates Removed:** {dups:,}  ({dup_rate:.2%})\n")
        W(f"- **Total Sentences:** {total_sents:,}\n")
        W(f"- **Total Words (tokens):** {total_words:,}\n")
        W(f"- **Total Characters:** {total_chars:,}\n")
        W(f"- **Total Bytes (UTF-8):** {total_bytes:,} (≈ {total_bytes/(1024**3):.2f} GB)\n\n")

        W("## 2. Vocabulary & Typology\n")
        W(f"- **Unique Word Types:** {unique:,}\n")
        W(f"- **Type-Token Ratio (TTR):** {ttr:.5f}\n")
        W(f"- **Hapax Legomena:** {hapax:,}\n")
        W(f"- **Hapax / Total Tokens:** {hapax/max(total_words,1):.5f}\n")
        W(f"- **Hapax / Unique Types:** {hapax/max(unique,1):.5f}\n\n")

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
        W(f"- **Devanagari Characters:** {dev_chars:,}\n")
        W(f"- **Latin Characters:** {lat_chars:,}\n")
        if ts: W(f"- **Ratio:** {dev_chars/ts:.2%} Devanagari / {lat_chars/ts:.2%} Latin\n")
        W(f"- **Other (punct, space, symbols):** {total_chars-dev_chars-lat_chars-asc_digits:,}\n\n")

        W("## 6. Digit Distribution (Devanagari vs ASCII)\n")
        W(f"- **Devanagari Digits (०–९):** {dev_digits:,}\n")
        W(f"- **ASCII Digits (0–9):** {asc_digits:,}\n")
        if td: W(f"- **Ratio:** {dev_digits/td:.2%} Devanagari / {asc_digits/td:.2%} ASCII\n")
        W("\n  > **LinguaBPE H3:** High Devanagari-digit ratio justifies numeral normalisation layer.\n\n")

        W("## 7. Halanta & Conjuncts\n")
        W(f"- **Halanta (् U+094D) Count:** {halanta:,}\n")
        if dev_chars: W(f"- **Halanta Density:** {halanta/dev_chars:.4%} of all Devanagari chars\n")
        W("  > **LinguaBPE H2:** Each Halanta = one conjunct vulnerable to byte-level fragmentation.\n\n")

        W("## 8. Suffix-bearing Words\n")
        W(f"- **Suffix-bearing Words:** {sufb:,} ({sufb/max(total_words,1):.2%} of total)\n")
        W("  > Longest-first matching: हरुको counted as हरुको, not को.\n")
        W("- **Per-suffix counts:**\n")
        for suf, cnt in sfreq.most_common(20):
            W(f"  - `{suf}`: {cnt:,}  ({cnt/max(sufb,1):.2%})\n")
        W("\n")

        W("## 9. Noise Rates\n")
        W(f"- **HTML Remnants:** {html_c:,}\n")
        W(f"- **URLs:** {url_c:,}\n")
        W(f"- **Phone Numbers:** {phone_c:,}\n")
        W(f"- **Emojis:** {emojis:,}\n\n")

        W("## 10. Top 50 Most Frequent Words\n")
        for word, cnt in wfreq.most_common(50):
            W(f"- `{word}`: {cnt:,}\n")

    print(f"\n✅ Report saved → {output_file}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    n_cores = multiprocessing.cpu_count()
    print(f"Cores: {n_cores}  |  Loading IRIIS corpus into RAM...")

    ds = load_dataset(
        "IRIIS-RESEARCH/Nepali-Text-Corpus",
        split="train",
        num_proc=n_cores,
    )
    print(f"Loaded: {len(ds):,} rows | {ds.column_names}\n")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "corpus_evaluation_report_corrected.md")
    generate_report(ds, output_file=out, n_proc=n_cores, batch_size=2000)