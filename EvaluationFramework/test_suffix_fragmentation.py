from tokenizer_eval_utils import get_tokenizer

def test_suffix_fragmentation():
    tokenizer = get_tokenizer()
    
    # Common Nepali root words and suffixes
    base_words = ["घर", "मानिस", "नेपाल", "राम", "काम", "किताब"]
    suffixes = ["मा", "लाई", "ले", "को", "का", "की", "बाट", "देखि", "हरूसँग"]
    
    print("=== Suffix Fragmentation Test ===")
    print("Checking if root+suffix tokenization drastically alters the root token.\n")
    
    bad_splits = 0
    total_checks = 0

    for base in base_words:
        base_tokens = tokenizer.tokenize(base, add_special_tokens=False)
        for suffix in suffixes:
            combined = base + suffix
            suff_tokens = tokenizer.tokenize(suffix, add_special_tokens=False)
            com_tokens = tokenizer.tokenize(combined, add_special_tokens=False)
            
            total_checks += 1
            
            # An ideal straightforward tokenizer might yield base_tokens + suff_tokens.
            # However, BPE might merge them, which is acceptable if it's efficient.
            # The danger is when base_tokens gets FRAGMENTED worse because of a suffix.
            # Example: 'घर' (1) + 'मा' (1) -> 'घ' 'र' 'मा' (3).
            
            is_fragmented = len(com_tokens) > len(base_tokens) + len(suff_tokens)
            
            if is_fragmented:
                print(f"❌ FRAGMENTATION: {base}({base_tokens}) + {suffix}({suff_tokens}) -> {combined}({com_tokens})")
                bad_splits += 1
            else:
                # Still show a few successful merges to illustrate BPE at work
                if total_checks % 10 == 0:
                    print(f"✅ OK: {base}({base_tokens}) + {suffix}({suff_tokens}) -> {combined}({com_tokens})")

    print(f"\nSummary: {bad_splits} fragmented root-suffix pairs out of {total_checks} checked.")

if __name__ == "__main__":
    test_suffix_fragmentation()