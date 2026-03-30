import argparse
import os
import unicodedata
from pathlib import Path
from transformers import AutoTokenizer

def normalize_text(text: str) -> str:
    """Normalize text into NFC form for consistent Devanagari byte sequences."""
    return unicodedata.normalize("NFC", text.strip())

def analyze_tokenization(tokenizer, word: str):
    """Tokenize a single word and return metadata."""
    token_ids = tokenizer.encode(word, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    
    # Check for Unknown tokens
    has_unk = any(t == tokenizer.unk_token for t in tokens if tokenizer.unk_token)
    
    return tokens, token_ids, len(token_ids), has_unk

def analyze_test_file(file_path: Path, tokenizer, verbose: bool):
    """Analyze a single test file containing Nepali words line-by-line."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [normalize_text(line) for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    if not lines:
        return None

    total_words = len(lines)
    total_tokens = 0
    words_with_unk = 0
    issue_words = []

    print(f"\n" + "="*50)
    print(f"📄 Analyzing File: {file_path.name}")
    print("="*50)

    for word in lines:
        tokens, token_ids, token_count, has_unk = analyze_tokenization(tokenizer, word)
        
        total_tokens += token_count
        if has_unk:
            words_with_unk += 1
            issue_words.append((word, tokens, "Contains UNK token"))
        
        # Consider a word heavily fragmented if it takes > 5 tokens for a single normal string length
        if token_count > 6 and len(word) < 15:
            issue_words.append((word, tokens, f"High fragmentation ({token_count} tokens)"))

        if verbose:
            print(f"Word: {word}")
            print(f"Tokens: {tokens} | Count: {token_count}")
            print("-" * 30)

    avg_tokens_per_word = total_tokens / total_words

    print(f"\n📊 Summary for {file_path.name}:")
    print(f"  - Total Words: {total_words}")
    print(f"  - Total Tokens: {total_tokens}")
    print(f"  - Average Tokens per Word: {avg_tokens_per_word:.2f}")
    print(f"  - Words with UNK tokens: {words_with_unk}")
    
    if issue_words and not verbose:
        print("\n⚠️ Potential Issues Detected (High fragmentation or UNKs):")
        for iw in issue_words[:5]: # Show up to 5 issues
            print(f"   [!] {iw[2]}: '{iw[0]}' -> {iw[1]}")
        if len(issue_words) > 5:
            print(f"   ... and {len(issue_words) - 5} more issues.")

    return {
        "file": file_path.name,
        "total_words": total_words,
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens_per_word,
        "unks": words_with_unk
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate a HuggingFace Tokenizer against a test suite of Nepali words.")
    parser.add_argument("--model-id", default="universalml/Nepali_Tokenizer", help="HuggingFace model/tokenizer ID")
    parser.add_argument("--test-dir", default="EvalTest", help="Directory containing .txt test files")
    parser.add_argument("--verbose", action="store_true", help="Print tokenization of every word")
    
    args = parser.parse_args()

    print(f"Loading Tokenizer: {args.model_id}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)

    test_dir = Path(args.test_dir)
    if not test_dir.exists() or not test_dir.is_dir():
        print(f"Error: Test directory '{test_dir}' not found.")
        return

    test_files = list(test_dir.glob("*.txt"))
    if not test_files:
        print(f"No .txt test files found in '{test_dir}'.")
        return

    results = []
    for test_file in test_files:
        res = analyze_test_file(test_file, tokenizer, args.verbose)
        if res:
            results.append(res)

    print("\n" + "#"*50)
    print("🏆 GLOBAL EVALUATION SUMMARY")
    print("#"*50)
    
    global_words = sum(r["total_words"] for r in results)
    global_tokens = sum(r["total_tokens"] for r in results)
    
    for r in results:
        print(f"- {r['file']}: {r['avg_tokens']:.2f} avg tokens/word | {r['unks']} UNKs")
        
    print(f"\nOverall Average: {global_tokens / global_words:.2f} tokens/word across {global_words} test cases.")

if __name__ == "__main__":
    main()
