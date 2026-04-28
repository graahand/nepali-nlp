import re
import math
import collections
from urllib.parse import urlparse
from datasets import load_dataset
from tqdm import tqdm
import unicodedata

def generate_report(ds, output_file="corpus_evaluation_report.md"):
    # 1. Basic Stats
    total_docs = 0
    total_sentences = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0

    # 2. Vocabulary
    word_freq = collections.Counter()
    
    # 3. Source/Domain
    domain_dist = collections.Counter()
    
    # 4. Length distributions
    doc_lengths_sentences = []
    doc_lengths_words = []
    sent_lengths_words = []
    
    # 5 & 6. Scripts & Digits
    devanagari_chars = 0
    latin_chars = 0
    devanagari_digits = 0
    ascii_digits = 0
    
    # 7. Halanta & Conjuncts
    halanta_count = 0
    
    # 8. Suffixes
    nepali_suffixes = ["ले", "लाई", "को", "का", "की", "मा", "बाट", "भन्दा", "हरू", "हरु", "सँग"]
    suffix_dist = collections.Counter()
    suffix_bearing_words = 0
    
    # 9. Duplicates
    seen_hashes = set()
    duplicate_docs = 0
    
    # 10. Noise
    html_tags_count = 0
    urls_count = 0
    phone_numbers_count = 0
    emojis_count = 0

    # Regex patterns
    sentence_split_pattern = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|।)\s')
    html_pattern = re.compile(r'<[^>]+>')
    url_pattern = re.compile(r'https?://[^\s]+')
    phone_pattern = re.compile(r'\b(?:\+977[- \.]?)?(?:98|97|96|01|0\d)[- \.]?\d{7,8}\b')

    print("Analyzing corpus...")
    # Get the keys of the first document to know the text column
    first_doc_keys = list(next(iter(ds)).keys())
    print("Dataset keys:", first_doc_keys)
    text_key = "text"
    
    # Try common case-insensitive variants
    lower_keys = [k.lower() for k in first_doc_keys]
    
    if "text" in lower_keys:
        text_key = first_doc_keys[lower_keys.index("text")]
    elif "content" in lower_keys:
        text_key = first_doc_keys[lower_keys.index("content")]
    elif "article" in lower_keys:
        text_key = first_doc_keys[lower_keys.index("article")]
    elif "body" in lower_keys:
        text_key = first_doc_keys[lower_keys.index("body")]
    else:
        # Avoid integers/indices
        for key in first_doc_keys:
            if key.lower() not in ['index', 'id']:
                text_key = key
                break
                
    print(f"Using '{text_key}' as the text column.")

    # Analyzing document by document
    for doc in tqdm(ds, desc="Processing Documents"):
        text = str(doc.get(text_key, ""))
        if not text:
            continue
            
        # Duplicates (exact match simulation via hash)
        doc_hash = hash(text)
        if doc_hash in seen_hashes:
            duplicate_docs += 1
            continue
        seen_hashes.add(doc_hash)

        # Basic doc stats
        total_docs += 1
        total_chars += len(text)
        total_bytes += len(text.encode('utf-8'))
        
        # Domain distribution
        url = doc.get("url", "")
        if url:
            domain = urlparse(url).netloc
            domain_dist[domain] += 1
        else:
            source = doc.get("source", "Unknown")
            domain_dist[source] += 1

        # Noise extraction
        html_tags_count += len(html_pattern.findall(text))
        urls_count += len(url_pattern.findall(text))
        phone_numbers_count += len(phone_pattern.findall(text))
        for char in text:
            if unicodedata.category(char) == 'So':  # Symbol, Other (includes many emojis)
                emojis_count += 1

        # Sentence split (assuming Nepali Purna Viram '।' or standard punctuation)
        sentences = sentence_split_pattern.split(text)
        total_sentences += len(sentences)
        doc_lengths_sentences.append(len(sentences))

        doc_word_count = 0
        for sent in sentences:
            words = sent.split()
            sent_word_count = len(words)
            sent_lengths_words.append(sent_word_count)
            doc_word_count += sent_word_count
            
            for word in words:
                word_clean = word.strip('.,?!।\'"()[]{}:;-')
                if not word_clean:
                    continue
                
                word_freq[word_clean] += 1
                
                # Check characters
                for char in word_clean:
                    code_point = ord(char)
                    # Devanagari Block (U+0900 - U+097F)
                    if 0x0900 <= code_point <= 0x097F:
                        devanagari_chars += 1
                        if 0x0966 <= code_point <= 0x096F:
                            devanagari_digits += 1
                        if code_point == 0x094D:  # Halanta
                            halanta_count += 1
                    # Latin Block
                    elif (0x0041 <= code_point <= 0x005A) or (0x0061 <= code_point <= 0x007A):
                        latin_chars += 1
                    # ASCII digits
                    elif 0x0030 <= code_point <= 0x0039:
                        ascii_digits += 1
                        
                # Check suffixes
                has_suffix = False
                for suffix in nepali_suffixes:
                    if word_clean.endswith(suffix) and len(word_clean) > len(suffix):
                        suffix_dist[suffix] += 1
                        has_suffix = True
                if has_suffix:
                    suffix_bearing_words += 1
                    
        doc_lengths_words.append(doc_word_count)
        total_words += doc_word_count

    # Calculations
    unique_words = len(word_freq)
    type_token_ratio = unique_words / max(total_words, 1)
    hapax_legomena = sum(1 for count in word_freq.values() if count == 1)
    hapax_ratio = hapax_legomena / max(total_words, 1)
    
    duplicate_rate = duplicate_docs / max(total_docs + duplicate_docs, 1)
    
    # Helper to calculate quantiles
    def get_stats(data):
        if not data:
            return {"min": 0, "q1": 0, "median": 0, "q3": 0, "max": 0, "mean": 0}
        s_data = sorted(data)
        n = len(s_data)
        return {
            "min": s_data[0],
            "q1": s_data[n//4],
            "median": s_data[n//2],
            "q3": s_data[3*n//4],
            "max": s_data[-1],
            "mean": sum(data) / n
        }

    doc_len_sent_stats = get_stats(doc_lengths_sentences)
    doc_len_word_stats = get_stats(doc_lengths_words)
    sent_len_word_stats = get_stats(sent_lengths_words)

    # ------------------ WRITING MARKDOWN REPORT ------------------
    print(f"Writing report to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Nepali Corpus Evaluation Report\n\n")
        
        f.write("## 1. Corpus Size Metrics\n")
        f.write(f"- **Total Documents:** {total_docs:,}\n")
        f.write(f"- **Total Sentences:** {total_sentences:,}\n")
        f.write(f"- **Total Words:** {total_words:,}\n")
        f.write(f"- **Total Characters:** {total_chars:,}\n")
        f.write(f"- **Total Bytes:** {total_bytes:,} (approx {total_bytes/(1024**2):.2f} MB)\n\n")

        f.write("## 2. Vocabulary & Typology\n")
        f.write(f"- **Unique Word Types:** {unique_words:,}\n")
        f.write(f"- **Type-Token Ratio (TTR):** {type_token_ratio:.5f}\n")
        f.write(f"- **Hapax Legomena:** {hapax_legomena:,}\n")
        f.write(f"- **Hapax Ratio:** {hapax_ratio:.5f}\n\n")

        f.write("## 3. Source/Domain Distribution\n")
        for domain, count in domain_dist.most_common(10):
            f.write(f"- **{domain}**: {count:,} documents\n")
        f.write("\n")

        f.write("## 4. Length Distributions\n")
        f.write("### Document Lengths (in Sentences)\n")
        f.write(f"- Mean: {doc_len_sent_stats['mean']:.2f} | Median: {doc_len_sent_stats['median']} | Max: {doc_len_sent_stats['max']}\n")
        f.write("### Document Lengths (in Words)\n")
        f.write(f"- Mean: {doc_len_word_stats['mean']:.2f} | Median: {doc_len_word_stats['median']} | Max: {doc_len_word_stats['max']}\n")
        f.write("### Sentence Lengths (in Words)\n")
        f.write(f"- Mean: {sent_len_word_stats['mean']:.2f} | Median: {sent_len_word_stats['median']} | Max: {sent_len_word_stats['max']}\n\n")

        f.write("## 5. Devanagari vs Latin Script Ratio\n")
        f.write(f"- **Devanagari Characters:** {devanagari_chars:,}\n")
        f.write(f"- **Latin Characters:** {latin_chars:,}\n")
        total_scripts = devanagari_chars + latin_chars
        if total_scripts > 0:
            f.write(f"- **Ratio:** {devanagari_chars / total_scripts:.2%} Devanagari / {latin_chars / total_scripts:.2%} Latin\n\n")

        f.write("## 6. Digit Distribution (Devanagari vs ASCII)\n")
        f.write(f"- **Devanagari Digits (०-९):** {devanagari_digits:,}\n")
        f.write(f"- **ASCII Digits (0-9):** {ascii_digits:,}\n")
        total_digits = devanagari_digits + ascii_digits
        if total_digits > 0:
            f.write(f"- **Ratio:** {devanagari_digits / total_digits:.2%} Devanagari / {ascii_digits / total_digits:.2%} ASCII\n\n")

        f.write("## 7. Halanta & Conjuncts\n")
        f.write(f"- **Halanta (्) Count:** {halanta_count:,}\n")
        f.write("  *(This approximates the occurrences of halanta-bearing conjunct characters.)*\n\n")

        f.write("## 8. Suffix-bearing Words\n")
        f.write(f"- **Suffix-bearing Words Count:** {suffix_bearing_words:,} ({(suffix_bearing_words/max(total_words,1)):.2%} of total words)\n")
        f.write("- **Top Suffix Chains/Occurrences:**\n")
        for suffix, count in suffix_dist.most_common(10):
            f.write(f"  - `{suffix}`: {count:,}\n")
        f.write("\n")

        f.write("## 9. Formatting & Duplication\n")
        f.write(f"- **Exact Duplicate Documents:** {duplicate_docs:,}\n")
        f.write(f"- **Duplicate Rate:** {duplicate_rate:.2%}\n\n")

        f.write("## 10. Noise Rates\n")
        f.write(f"- **HTML Elements Remnants:** {html_tags_count:,}\n")
        f.write(f"- **URLs Found:** {urls_count:,}\n")
        f.write(f"- **Phone Numbers Detected:** {phone_numbers_count:,}\n")
        f.write(f"- **Emojis Found:** {emojis_count:,}\n")
        
    print(f"Done! Report saved to '{output_file}'.")

if __name__ == '__main__':
    import os
    # Adjust `split="train"` if needed, or iterate over train/test splits.
    dataset = load_dataset("IRIIS-RESEARCH/Nepali-Text-Corpus", split="train")
    # Save the report in the same directory as this script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.md")
    generate_report(dataset, output_file=output_path)


