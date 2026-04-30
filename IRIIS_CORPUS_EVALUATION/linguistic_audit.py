"""
linguistic_audit.py  —  LINGUA-NEP A1 / A2 / A3 Audit
=======================================================
Extracts the morphological, conjunct, and numeral statistics
required to validate all four LinguaBPE hypotheses.

Run AFTER corpus_evaluation_report.py (dataset is already cached).

Usage:
    python linguistic_audit.py

Output:
    linguistic_audit_report.md
    linguistic_audit_data.json   ← raw numbers for downstream use
"""

import re
import os
import json
import hashlib
import collections
import multiprocessing
from datasets import load_dataset
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# A1 — Morphological inventory
# ─────────────────────────────────────────────────────────────────────────────

# Extended suffix list — 80 candidates covering all productive Nepali morphology.
# Ordered longest-first for greedy chain stripping.
ALL_SUFFIXES = sorted([
    # Agglutinative verb chains (proposal super-suffix candidates)
    "गरिरहेकाले", "गरिरहेकोले", "गरिरहेको", "गरिरहेका",
    "भइसकेकाले", "भइसकेको", "गरिसकेकाले", "गरिसकेको",
    "हुँदैगर्दा", "गर्दैगर्दा",
    # Plural + case chains
    "हरुलाई", "हरुबाट", "हरुसँग", "हरुसँगै", "हरुको",
    "हरुका", "हरुकी", "हरुले", "हरुमा", "हरुमात्र",
    "हरूलाई", "हरूबाट", "हरूसँग", "हरूको", "हरूका",
    "हरूकी", "हरूले", "हरूमा",
    # Tense/aspect suffixes
    "इरहेको", "इसकेको", "इरहेका", "इसकेका",
    "दैछन्", "दैछ", "दैथ्यो", "दैथिए",
    "नुभयो", "नुभए", "नुहुन्छ", "नुपर्छ", "नुपर्ने",
    "एकोले", "एकोमा", "एकोका", "एकाले",
    # Pure plural
    "हरू", "हरु",
    # Vibhakti (case markers) — longest first within this group
    "सँगसँगै", "सँगै", "सँग",
    "भन्दा", "देखि", "सम्म", "तिर", "भित्र",
    "माथि", "तल", "अगि", "पछि", "नेर", "थरी",
    "बाट", "लाई", "मात्र", "नै", "चाहिँ",
    "मा", "ले", "को", "का", "की",
    # Emphatic / focus
    "पनि", "नि", "त",
], key=len, reverse=True)

# Suffix chains to track explicitly (proposal §3.3.3 super-suffixes)
SUPER_SUFFIX_CANDIDATES = [
    "हरुलाई", "हरुबाट", "हरुसँग", "हरुको", "हरुले", "हरुमा",
    "भइसकेको", "भइसकेकाले", "गरिरहेको", "गरिरहेकाले",
    "गरिसकेको", "गरिसकेकाले",
    "नुपर्छ", "नुहुन्छ", "नुभयो",
    "दैछन्", "दैछ", "एकोले", "एकाले",
]

# ─────────────────────────────────────────────────────────────────────────────
# A2 — Conjunct inventory
# ─────────────────────────────────────────────────────────────────────────────

# Halanta (virama) U+094D — joins consonants into conjuncts
HALANTA = "\u094D"

# Devanagari consonant range
CONSONANT_RE = re.compile(
    r"[\u0915-\u0939\u0958-\u095F\u0900-\u0903]"   # ka–ha + nukta forms
)

# Extract all [C + ् + C] and [C + ् + C + ् + C] sequences
CONJUNCT_RE = re.compile(
    r"(?:[\u0915-\u0939\u0958-\u095F]"   # consonant
    r"\u094D"                              # halanta
    r")+"                                  # one or more [C+halanta] prefix
    r"[\u0915-\u0939\u0958-\u095F]"       # final consonant (no halanta)
)

# High-priority conjuncts from the proposal
PRIORITY_CONJUNCTS = [
    "क्ष", "त्र", "ज्ञ", "श्र", "स्त्र", "त्म", "द्र", "प्र", "ब्र",
    "क्त", "ग्र", "भ्र", "म्र", "स्त", "स्थ", "न्त", "न्द", "ण्ड",
    "ट्ट", "ड्ड", "च्च", "च्छ", "द्ध", "त्त", "क्क", "ल्ल",
    "द्व", "द्य", "ह्र", "ह्व", "ह्य", "स्व", "स्म", "स्प",
]

# ─────────────────────────────────────────────────────────────────────────────
# A3 — Numeral inventory
# ─────────────────────────────────────────────────────────────────────────────

# Span patterns
DEV_SPAN_RE  = re.compile(r"[०-९]+")
ASCII_SPAN_RE = re.compile(r"[0-9]+")

# Phone: 9-10 consecutive Devanagari or ASCII digits (Nepali mobile format)
PHONE_DEV_RE = re.compile(r"(?<![०-९])[९८][०-९]{8,9}(?![०-९])")
PHONE_ASC_RE = re.compile(r"(?<![0-9])(?:98|97|96|01)[0-9]{7,8}(?![0-9])")

# Dates: various Nepali date formats
DATE_RE = re.compile(
    r"[०-९]{4}[/।\-][०-९]{1,2}[/।\-][०-९]{1,2}"   # २०२६/०४/२७
    r"|[0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}"          # 2026-04-27
    r"|[०-९]{1,2}[/।\-][०-९]{1,2}[/।\-][०-९]{2,4}"   # DD/MM/YYYY dev
    r"|[०-९]{4}\s*(?:साल|सन्|वि\.सं\.?|बि\.सं\.?)"   # २०८१ साल
    r"|[0-9]{4}\s*(?:AD|BC|CE)"
)

# Currency: रु, Rs, $, £, ¥ followed by digits
CURRENCY_RE = re.compile(
    r"(?:रु\.?\s*|रुपैयाँ\s*|Rs\.?\s*|\$|£|¥|€)"
    r"[०-९0-9][०-९0-9,\.]*"
    r"|[०-९0-9][०-९0-9,\.]*\s*(?:रुपैयाँ|रुपया)"
)

# Percentages
PERCENT_RE = re.compile(
    r"[०-९0-9][०-९0-9\.]*\s*(?:%|प्रतिशत|प्रति\s*शत)"
)

# Mixed numeral spans (Devanagari + ASCII in same token, e.g. २०२६/04/27)
MIXED_RE = re.compile(r"(?:[०-९]+[०-९0-9\-/\.]*[0-9]+|[0-9]+[0-9०-९\-/\.]*[०-९]+)")

# ─────────────────────────────────────────────────────────────────────────────
# Suffix chain stripper
# ─────────────────────────────────────────────────────────────────────────────

def strip_suffix_chain(word: str, suffix_list: list) -> tuple[str, list]:
    """
    Greedily strip suffixes from a word, returning (stem, [suffixes_stripped]).
    Stops when no suffix matches or word is too short.
    """
    chain = []
    current = word
    for _ in range(6):   # max chain depth = 6 morphemes
        matched = False
        for suf in suffix_list:
            if current.endswith(suf) and len(current) > len(suf) + 1:
                chain.append(suf)
                current = current[: -len(suf)]
                matched = True
                break
        if not matched:
            break
    return current, chain

# ─────────────────────────────────────────────────────────────────────────────
# Batch worker
# ─────────────────────────────────────────────────────────────────────────────

TEXT_COL = "Article"

def audit_batch(batch: dict) -> dict:
    # A1
    suffix_token_freq  = collections.Counter()   # suffix → token occurrences
    chain_freq         = collections.Counter()   # full chain string → occurrences
    chain_lengths      = []                      # list of chain-depth ints
    suffix_type_set    = set()                   # unique word types with a suffix
    total_word_types   = set()                   # unique word types seen

    # A2
    conjunct_freq      = collections.Counter()   # conjunct string → occurrences

    # A3
    dev_spans = asc_spans = 0
    dev_span_lengths = []
    asc_span_lengths = []
    phone_count = date_count = currency_count = percent_count = mixed_count = 0

    for text in batch[TEXT_COL]:
        if not text:
            continue
        text = str(text)

        # ── A2: conjunct extraction (on raw text, most efficient) ──────────────
        for m in CONJUNCT_RE.finditer(text):
            conjunct_freq[m.group()] += 1

        # ── A3: numeral spans ──────────────────────────────────────────────────
        for m in DEV_SPAN_RE.finditer(text):
            dev_spans += 1
            dev_span_lengths.append(len(m.group()))
        for m in ASCII_SPAN_RE.finditer(text):
            asc_spans += 1
            asc_span_lengths.append(len(m.group()))

        phone_count    += len(PHONE_DEV_RE.findall(text)) + len(PHONE_ASC_RE.findall(text))
        date_count     += len(DATE_RE.findall(text))
        currency_count += len(CURRENCY_RE.findall(text))
        percent_count  += len(PERCENT_RE.findall(text))
        mixed_count    += len(MIXED_RE.findall(text))

        # ── A1: word-level morphology ──────────────────────────────────────────
        for word in text.split():
            w = word.strip(".,?!\u0964\u0965'\u2018\u2019\"\u201c\u201d()[]{}:;-\u2013\u2014")
            if not w or len(w) < 3:
                continue
            total_word_types.add(w)

            stem, chain = strip_suffix_chain(w, ALL_SUFFIXES)
            if chain:
                suffix_type_set.add(w)
                for suf in chain:
                    suffix_token_freq[suf] += 1
                chain_key = "+".join(chain)
                chain_freq[chain_key] += 1
                chain_lengths.append(len(chain))

    # Serialise counters as JSON strings to avoid Arrow schema conflicts
    return {
        "_suf_freq":    [json.dumps(dict(suffix_token_freq.most_common(200)), ensure_ascii=False)],
        "_chain_freq":  [json.dumps(dict(chain_freq.most_common(500)), ensure_ascii=False)],
        "_chain_lens":  [json.dumps(chain_lengths)],
        "_n_types":     [len(total_word_types)],
        "_n_suf_types": [len(suffix_type_set)],
        "_conj_freq":   [json.dumps(dict(conjunct_freq.most_common(500)), ensure_ascii=False)],
        "_dev_spans":   [dev_spans],
        "_asc_spans":   [asc_spans],
        "_dev_sl":      [json.dumps(dev_span_lengths)],
        "_asc_sl":      [json.dumps(asc_span_lengths)],
        "_phones":      [phone_count],
        "_dates":       [date_count],
        "_currency":    [currency_count],
        "_percent":     [percent_count],
        "_mixed":       [mixed_count],
    }

# ─────────────────────────────────────────────────────────────────────────────
# Reduce helpers
# ─────────────────────────────────────────────────────────────────────────────

def mean(lst):
    return round(sum(lst) / len(lst), 3) if lst else 0.0

def get_stats(lst):
    if not lst:
        return {"mean": 0, "median": 0, "max": 0, "min": 0}
    s = sorted(lst)
    n = len(s)
    return {"mean": round(sum(s)/n, 3), "median": s[n//2], "max": s[-1], "min": s[0]}

# ─────────────────────────────────────────────────────────────────────────────
# Report writer
# ─────────────────────────────────────────────────────────────────────────────

def write_report(data: dict, output_md: str, output_json: str):
    # Save raw JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Raw data → {output_json}")

    sf   = data["suffix_token_freq"]      # list of (suffix, count)
    cf   = data["chain_freq"]             # list of (chain, count)
    conj = data["conjunct_freq"]          # list of (conjunct, count)

    total_suffix_tokens = sum(c for _, c in sf)
    total_chain_tokens  = sum(c for _, c in cf)
    total_conj_tokens   = sum(c for _, c in conj)

    with open(output_md, "w", encoding="utf-8") as f:
        W = f.write

        W("# LINGUA-NEP Linguistic Audit Report\n")
        W("*A1 Morphological · A2 Conjunct · A3 Numeral inventories*\n\n")

        # ── A1 ─────────────────────────────────────────────────────────────────
        W("## A1. Morphological Inventory\n\n")

        W("### A1.1 Suffix token frequencies (top-50)\n")
        W("*Each word contributes one count per suffix stripped in its chain.*\n\n")
        W("| Rank | Suffix | Token occurrences | % of suffix tokens |\n")
        W("|------|--------|-------------------|--------------------|\n")
        for i, (suf, cnt) in enumerate(sf[:50], 1):
            pct = cnt / max(total_suffix_tokens, 1) * 100
            W(f"| {i} | `{suf}` | {cnt:,} | {pct:.2f}% |\n")
        W("\n")

        W("### A1.2 Top-200 suffix chains\n")
        W("*A chain is the full sequence of suffixes stripped from one word, e.g. हरु+लाई.*\n\n")
        W("| Rank | Chain | Count |\n")
        W("|------|-------|-------|\n")
        for i, (chain, cnt) in enumerate(cf[:200], 1):
            W(f"| {i} | `{chain}` | {cnt:,} |\n")
        W("\n")

        cls = data["chain_length_stats"]
        W("### A1.3 Suffix-chain length statistics\n")
        W(f"- **Mean chain depth:** {cls['mean']} morphemes\n")
        W(f"- **Median chain depth:** {cls['median']} morphemes\n")
        W(f"- **Max chain depth:** {cls['max']} morphemes\n")
        W(f"- **Total words with ≥1 suffix:** {data['total_suffix_token_words']:,}\n\n")

        W("### A1.4 Word-type coverage\n")
        W(f"- **Unique word types sampled:** {data['total_word_types_sampled']:,}\n")
        W(f"- **Types ending in productive suffix:** {data['suffix_bearing_types']:,}\n")
        pct_types = data['suffix_bearing_types'] / max(data['total_word_types_sampled'], 1) * 100
        W(f"- **Coverage:** {pct_types:.2f}%\n\n")

        W("### A1.5 Super-suffix candidate frequencies\n")
        W("*(Proposal §3.3.3 — candidates for pre-injection as single vocabulary tokens)*\n\n")
        W("| Super-suffix | Count |\n")
        W("|---|---|\n")
        sf_dict = dict(sf)
        for ss in SUPER_SUFFIX_CANDIDATES:
            cnt = sf_dict.get(ss, 0)
            W(f"| `{ss}` | {cnt:,} |\n")
        W("\n")

        # ── A2 ─────────────────────────────────────────────────────────────────
        W("## A2. Conjunct Inventory\n\n")
        W(f"- **Distinct conjunct types:** {data['distinct_conjunct_types']:,}\n")
        W(f"- **Total conjunct token occurrences:** {total_conj_tokens:,}\n\n")

        W("### A2.1 Top-100 conjuncts by frequency\n\n")
        W("| Rank | Conjunct | Token count | % of conjuncts |\n")
        W("|------|----------|-------------|----------------|\n")
        for i, (conj_str, cnt) in enumerate(conj[:100], 1):
            pct = cnt / max(total_conj_tokens, 1) * 100
            W(f"| {i} | `{conj_str}` | {cnt:,} | {pct:.3f}% |\n")
        W("\n")

        W("### A2.2 Priority conjuncts (proposal list)\n\n")
        W("| Conjunct | Count | In top-100? |\n")
        W("|----------|-------|-------------|\n")
        conj_dict = dict(conj)
        top100_set = {c for c, _ in conj[:100]}
        for pc in PRIORITY_CONJUNCTS:
            cnt = conj_dict.get(pc, 0)
            in_top = "✓" if pc in top100_set else "—"
            W(f"| `{pc}` | {cnt:,} | {in_top} |\n")
        W("\n")

        W("> **Note for LinguaBPE H2:** The distinct conjunct count and per-conjunct frequencies\n")
        W("> establish the empirical scope of Halanta-Locking. Average token fragmentation per conjunct\n")
        W("> requires running each tokenizer — see the tokenizer evaluation suite.\n\n")

        # ── A3 ─────────────────────────────────────────────────────────────────
        W("## A3. Numeral Inventory\n\n")

        ds_stats  = data["dev_span_stats"]
        as_stats  = data["asc_span_stats"]
        total_spans = data["dev_spans"] + data["asc_spans"]

        W("### A3.1 Numeral spans\n")
        W(f"- **Devanagari-digit spans:** {data['dev_spans']:,}\n")
        W(f"- **ASCII-digit spans:** {data['asc_spans']:,}\n")
        W(f"- **Total spans:** {total_spans:,}\n")
        if total_spans:
            W(f"- **Dev/ASCII span ratio:** {data['dev_spans']/max(data['asc_spans'],1):.1f} : 1\n\n")

        W("### A3.2 Span length statistics\n")
        W("| Metric | Devanagari spans | ASCII spans |\n")
        W("|--------|-----------------|-------------|\n")
        W(f"| Mean length | {ds_stats['mean']} | {as_stats['mean']} |\n")
        W(f"| Median length | {ds_stats['median']} | {as_stats['median']} |\n")
        W(f"| Max length | {ds_stats['max']} | {as_stats['max']} |\n\n")

        W("### A3.3 Numeral category breakdown\n")
        W(f"- **Phone numbers:** {data['phones']:,}\n")
        W(f"- **Dates:** {data['dates']:,}\n")
        W(f"- **Currency expressions:** {data['currency']:,}\n")
        W(f"- **Percentages:** {data['percent']:,}\n")
        W(f"- **Mixed Dev+ASCII spans:** {data['mixed']:,}\n\n")

        W("> **Note for LinguaBPE H3:** The Devanagari/ASCII span ratio and the\n")
        W("> span-length distribution quantify the tokenization inefficiency that\n")
        W("> numeral normalisation will fix. A span of length N currently costs\n")
        W("> N/3 to N byte-level tokens; after normalisation it costs ⌈N/4⌉ BPE tokens.\n")

    print(f"  Report → {output_md}")

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_audit(ds, n_proc=None, batch_size=2000):
    n_proc = n_proc or multiprocessing.cpu_count()
    print(f"\nRunning linguistic audit: {len(ds):,} rows | {n_proc} workers\n")

    res = ds.map(
        audit_batch,
        batched=True,
        batch_size=batch_size,
        num_proc=n_proc,
        remove_columns=ds.column_names,
        desc="Auditing",
    )

    print("Reducing...")

    # A1
    suffix_freq  = collections.Counter()
    chain_freq   = collections.Counter()
    chain_lengths_all = []
    total_word_types_sampled = 0
    suffix_bearing_types     = 0
    total_suffix_token_words = 0

    # A2
    conjunct_freq = collections.Counter()

    # A3
    dev_spans = asc_spans = 0
    dev_sl_all, asc_sl_all = [], []
    phones = dates = currency = percent = mixed = 0

    for i in tqdm(range(len(res)), desc="Merging"):
        row = res[i]
        suffix_freq.update(json.loads(row["_suf_freq"]))
        chain_freq.update(json.loads(row["_chain_freq"]))
        cl = json.loads(row["_chain_lens"])
        chain_lengths_all.extend(cl)
        total_suffix_token_words += sum(cl)   # each entry = 1 word with ≥1 suffix
        total_word_types_sampled += row["_n_types"]
        suffix_bearing_types     += row["_n_suf_types"]
        conjunct_freq.update(json.loads(row["_conj_freq"]))
        dev_spans += row["_dev_spans"]
        asc_spans += row["_asc_spans"]
        dev_sl_all.extend(json.loads(row["_dev_sl"]))
        asc_sl_all.extend(json.loads(row["_asc_sl"]))
        phones   += row["_phones"]
        dates    += row["_dates"]
        currency += row["_currency"]
        percent  += row["_percent"]
        mixed    += row["_mixed"]

    data = {
        # A1
        "suffix_token_freq":          suffix_freq.most_common(200),
        "chain_freq":                 chain_freq.most_common(500),
        "chain_length_stats":         get_stats(chain_lengths_all),
        "total_suffix_token_words":   total_suffix_token_words,
        "total_word_types_sampled":   total_word_types_sampled,
        "suffix_bearing_types":       suffix_bearing_types,
        # A2
        "conjunct_freq":              conjunct_freq.most_common(500),
        "distinct_conjunct_types":    len(conjunct_freq),
        # A3
        "dev_spans":    dev_spans,
        "asc_spans":    asc_spans,
        "dev_span_stats": get_stats(dev_sl_all),
        "asc_span_stats": get_stats(asc_sl_all),
        "phones":    phones,
        "dates":     dates,
        "currency":  currency,
        "percent":   percent,
        "mixed":     mixed,
    }
    return data


if __name__ == "__main__":
    n_cores = multiprocessing.cpu_count()
    print(f"Cores: {n_cores} | Loading IRIIS corpus...")

    ds = load_dataset(
        "IRIIS-RESEARCH/Nepali-Text-Corpus",
        split="train",
        num_proc=n_cores,
    )
    print(f"Loaded: {len(ds):,} rows\n")

    here = os.path.dirname(os.path.abspath(__file__))
    data = run_audit(ds, n_proc=n_cores, batch_size=2000)

    write_report(
        data,
        output_md=os.path.join(here, "linguistic_audit_report.md"),
        output_json=os.path.join(here, "linguistic_audit_data.json"),
    )
    print("\n✅ Done.")