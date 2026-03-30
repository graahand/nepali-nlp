import unicodedata
from pathlib import Path

def get_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("universalml/Nepali_Tokenizer", trust_remote_code=True)

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())

def analyze_file(tokenizer, filename: str):
    file_path = Path(__file__).parent / "EvalTest" / filename
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        words = [normalize_text(line) for line in f if line.strip()]
        
    total_tokens = 0
    issue_words = []
    
    print(f"=== Evaluation for {filename} ===")
    for word in words:
        tokens = tokenizer.tokenize(word, add_special_tokens=False)
        total_tokens += len(tokens)
        
        has_unk = any(t == tokenizer.unk_token for t in tokens if tokenizer.unk_token)
        if len(tokens) > 5 or has_unk:
            issue_words.append((word, tokens, "UNK" if has_unk else f"Long ({len(tokens)})"))

    avg = total_tokens / len(words) if words else 0
    print(f"Total Words: {len(words)}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Avg Tokens/Word: {avg:.2f}")
    if issue_words:
        print("\nWarnings:")
        for w, t, i in issue_words[:10]:
            print(f" [{i}] {w} -> {t}")
        if len(issue_words) > 10:
            print(f"... and {len(issue_words)-10} more.")
    print("================================\n")
