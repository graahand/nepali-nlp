import unicodedata
from tokenizer_eval_utils import get_tokenizer

def test_normalization():
    tokenizer = get_tokenizer()
    
    # Text that often causes issues between NFC and NFD (e.g., Devanagari with halantas and nukta)
    words = [
        "संविधान", # samvidhan
        "किंवदन्ती", # kimvadanti
        "अँध्यारो", # andhyaro
        "विज्ञान", # vigyan
        "डँडाल्नो", # dandalno
        "क्षमता", # kshamata
    ]
    
    print("=== Unicode Normalization Consistency Test ===")
    
    inconsistencies_found = 0
    for w in words:
        nfc_form = unicodedata.normalize("NFC", w)
        nfd_form = unicodedata.normalize("NFD", w)
        
        nfc_tokens = tokenizer.tokenize(nfc_form, add_special_tokens=False)
        nfd_tokens = tokenizer.tokenize(nfd_form, add_special_tokens=False)
        
        print(f"\nWord: {w}")
        print(f" NFC tokens ({len(nfc_tokens)}): {nfc_tokens}")
        print(f" NFD tokens ({len(nfd_tokens)}): {nfd_tokens}")
        
        if nfc_tokens != nfd_tokens:
            print(" ❌ Mismatch detected!")
            inconsistencies_found += 1
        else:
            print(" ✅ Match (Consistent)")
            
    print(f"\nTotal Inconsistent Words: {inconsistencies_found} / {len(words)}")

if __name__ == "__main__":
    test_normalization()