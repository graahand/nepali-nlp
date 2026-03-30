
# Novel NLP Research Directions for Nepali Language (SMAC)

## Overview
This document outlines the unique challenges, linguistic features, and research gaps in developing advanced Natural Language Processing (NLP) systems for the Nepali language, with a focus on Devanagari script. It also summarizes the progress made so far and highlights areas for future research.

## Key Research Directions

- Nepali Text-to-Speech (TTS):  
    Develop natural and expressive TTS systems tailored for Nepali.
    
- Nepali Speech-to-Text (STT):  
    Fine-tune models like Whisper using curated Nepali datasets for accurate speech recognition.
    
- Nepali Large Language Models (LLMs):  
    Build LLMs with robust reasoning abilities, specifically trained on Nepali data.
    
- Custom Nepali Tokenizer:  
    Create a tokenizer that treats Devanagari words as single tokens, unlike general-purpose tokenizers (e.g., ChatGPT, Llama) that fragment Nepali text.
    
- Morphological Tools:  
    Develop stemmers and lemmatizers to handle Nepali’s agglutinative morphology and complex suffixation.
    

## Linguistic Features & Complexities in Nepali (Devanagari Script)

- Distinct Letters:
    

- 36 consonants (33 unique, 3 combinations)
    
- 13 vowels, 10 numerals
    
- No capital letters; written left-to-right
    

- Agglutinative Morphology:  
    Suffixes attach to roots (e.g., घर + मा = घरमा).
    
- Postpositions:  
    Nepali uses postpositions (attached to nouns) instead of English prepositions.
    
- Honorifics:  
    Multiple levels (low, middle, high, royal) affecting subject-verb agreement.
    
- Word Order:  
    Nepali uses SOV (Subject-Object-Verb) order, unlike English SVO.
    
- Complex Ligatures:  
    Half letters, conjuncts, sibilants, and double half letters are common.
    
- Unicode Normalization:  
    Different ways of typing the same character (e.g., halant vs. conjunct) must be normalized.
    
- No Capitalization:  
    Nepali script does not use capital letters.
    

## Devanagari Script Features

|                          |                                                    |
| ------------------------ | -------------------------------------------------- |
| Feature                  | Example(s) / Explanation                           |
| Chandrabindu (ँ)         | बाँस (bamboo), चाँद (moon)                         |
| Sirbindu (ं)             | अंश (part), संसार (world)                          |
| Diacritics (Halanta - ्) | बस् (stop/sit - consonant sound cut short)         |
| Ref / Reph (र्)          | किर्ति (kirti), कर्म (karma)                       |
| Half Letters             | सुरेन्द्र (surendra - half न 'न्' with द)          |
| Double Letters           | सट्टा (satta - 'ट्ट'), बच्चा (bachha - 'च्च')      |
| Conjunct Characters      | श्रद्धा (shraddha - 'द्ध'), विद्या (vidya - 'द्य') |
| Sibilants                | समय (samaya), शहर (shahar), षड्यन्त्र (shadyantra) |
| Double Half Letter       | हुन्थ्यो (hunthyo - 'न्थ्य')                       |
| श्र                      | श्रम (shram - श् + र)                              |
| ऐ                        | ऐना (aaina - pronounced 'A-ee')                    |
| Similar Sounding Letters | वन (van - forest) vs. बन (ban - make/become)       |

## NLP Tasks & Tools

|   |   |
|---|---|
|Task/Tool|Description & Example|
|Tokenization|Splitting sentences into words: "म भात खान्छु" → ["म", "भात", "खान्छु"]|
|Morphological Analysis|घरमा (gharma) → Stem: घर (ghar), Suffix: मा (ma)|
|Stemming|Removes affixes: घरमा → घर|
|Lemmatization|Maps inflected forms to base: खाएँ (khāẽ) → खाना (khānā)|
|Named Entity Recognition|राम काठमाडौँ गयो। → राम (Person), काठमाडौँ (Location)|
|Word Sense Disambiguation|पत्र: letter (हुलाकको पत्र), leaf (रुखको पत्र)|
|Stop Words Removal|छ, छैन, हुन्छ, हुदैन, र, पनि|
|Anaphora Resolution|"CAT ATE THE MAT AND IT IS STILL HUNGRY" → "IT" refers to "CAT"|
|PoS Tagging|Assigning noun, pronoun, adjective, etc.|
|Agglutinative Morphology|घर + मा = घरमा (in the house), घर + लाई = घरलाई (to the house)|
|Affixes|Prefix: प्रगत (प्र + गत), Suffix: घरलाई (घर + लाई), Affix: असफलता (अ + सफल + ता)|
|Ligatures|क्ष (क् + ष): क्षमा, त्र (त् + र): त्रिशूल, ज्ञ (ज् + ञ): ज्ञान|

## Progress in Nepali NLP

- Bhasha Sanchar Project:  
    Led by Dr. Bal Krishna Bal (KU), pioneering Nepali NLP.
    
- Dobhase:  
    English-Nepali translation system.
    
- NepaLinux:  
    Nepali desktop environment with technical terms.
    
- Word Embeddings:  
    Rabindra Lamsal’s pre-trained vectors (fastText, Word2Vec).
    
- NepBERTa:  
    Nepali BERT for NER and sentiment analysis.
    
- OpenSLR 43 & 143:  
    Speech datasets.
    
- NepaliGPT:  
    Sushant Pudasaini’s autoregressive models.
    
- NLUE Benchmark:  
    Nepali Language Understanding Evaluation.
    
- Nep-lish:  
    Code-mixed Nepali-English remains a challenge.
    
- Legal & Medical NLP:  
    Frontier models are lacking.
    

## Gaps & Open Questions

#### 1. The Tokenization Gap

**Does the existing Nepali tokenizer actually tokenize the Nepali script correctly?**

No, most general-purpose tokenizers (like those used by ChatGPT or Llama) fail to tokenize Devanagari meaningfully.

- **Meaningless Fragments:** Standard tokenizers often break down a single Devanagari word into "meaningless pieces". For example, a word like **"हुन्थ्यो"** (containing a double-half alphabet 'न्थ्य') might be split into 4 or 5 sub-tokens **based on raw byte frequency rather than linguistic logic.**
    
- **Specific Failures:** Existing general tokenizers do not explicitly address the difference between similar characters like **'व'** and **'ब'**, nor do they consistently handle **diacritics** (halanta, chandrabindu), **half letters**, or **complex conjuncts** like **'द्ध'** or **'श्र'**.
    
- **Existing Research Approach**:  This research points to a **custom 16k Byte-Pair Encoding (BPE) tokenizer** trained exclusively on 8 million characters of Nepali text. This ensures more consistent segmentation by treating Devanagari units more holistically.

#### 2. Embedding Models and Morphological Semantics

**Are existing embedding models capable of capturing complex Nepali semantics?**

Current open-source multilingual embedding models often struggle with the **agglutinative nature** of Nepali.

- **The Agglutination Challenge:** In Nepali, suffixes are attached directly to roots (e.g., **"घर" + "लाई" = "घरलाई"**). Without a dedicated **Stemmer** or **Lemmatizer**, an embedding model might see "घर" and "घरलाई" as two unrelated vectors rather than versions of the same concept.
    
- **Semantic Proximity:** For effective contrastive learning, words with complex features—like **ref (र्)**, **sibilants (स, श, ष)**, and **half-letters**—must be mapped to nearby coordinates. While older models like **fastText** (Rabindra Lamsal) used sub-word information to help with this, they still lacked the deep contextual reasoning of modern Transformers.
    
- **Current State:** While progress exists (like **NepBERTa**), there is still a significant gap in capturing the nuanced semantics of honorifics and postpositions in a truly language-independent vector space.

#### 3. The Token Dilution Problem (Attention Mechanism)

**How does splitting Devanagari into multiple tokens affect the context window?**

This is a critical bottleneck. Because Devanagari words are often split into 3–4 tokens due to vowels and consonants, the **"Token Dilution"** effect occurs.

- **Context Exhaustion:** If an English sentence takes 10 tokens and the equivalent Nepali sentence takes 30, the model’s context window is effectively reduced by 66%.
    
- **Information Density:** The attention mechanism fills up with these sub-word fragments, meaning the model "remembers" less of the overall conversation or document compared to English.
    

#### 4. SOV vs. SVO: The Long-Term Dependency Challenge

**Can standard attention handle the Subject-Object-Verb (SOV) structure?**

Nepali’s **SOV structure** puts the verb at the very end of the sentence.

- **Dependency Stress:** The attention mechanism must hold the "Subject" in its active memory across the entire sentence to ensure the **Verb** at the end agrees in terms of respect level (low, middle, high, royal) and gender.

- **Agreement Conflicts:** If the attention span is too diluted by sub-word tokens, the model is more likely to cause **Subject-Verb Agreement** errors, a common issue in Devanagari LLM outputs.
#### 5. Architectural Changes vs. Pre-training

**Does the attention mechanism require architectural changes for Devanagari?**

While standard Transformers _can_ learn these patterns through sheer scale, **architectural tuning** is often more efficient for low-resource languages like Nepali.

- **Tuning with Corpus:** High-quality pre-training on a **curated Nepali dataset** (like the **Nepali National Corpus** with 14 million words) helps the model learn the "Ukhan/Tukka" and grammatical nuances.
    
- **Architectural Shifts:** Changes like **Rotary Position Embeddings (RoPE)**, but the **Attention Mechanism itself** may benefit from "Global-Local" attention patterns to better capture long-distance SOV dependencies without getting lost in the "diluted" tokens.
    
- **Ligature Addressing:** Handling complex ligatures like **'क्ष' (क् + ष)** often requires the model to treat these as single visual/semantic units during the embedding phase rather than separate characters.

### Comparison of Nepali vs. English NLP Architecture

|**Feature**|**English (SVO)**|**Nepali (SOV)**|
|---|---|---|
|**Token Density**|High (1 word $\approx$ 1 token)|Low (1 word $\approx$ 3+ tokens)|
|**Word Structure**|Prepositions ("to the house")|Agglutinative ("घरलाई")|
|**Key Challenge**|Syntax|Morphology & Honorifics|
|**Attention Goal**|Local Context|Long-distance Verb Agreement|

## Datasets & Resources

- Nepali National Corpus (NNC):  
    14M+ words, with monolingual, parallel, and spoken sub-corpora.
    
- 16NepaliNews:  
    14,364 documents, 16 classes.
    
- Nepali News Large Dataset:  
    7,023 documents, 20 genres.
    
- NepBERTa Corpus:  
    [NepBERTa Pre-training Corpus](https://drive.google.com/drive/folders/1oLvfKb663wZuw-n36ymHsSYAqeSHmKzo)
    
- OSCAR Dataset:  
    Contains highly duplicate/repeated data.
    
- Custom BPE Tokenizer:  
    16,384 vocab size, trained on 8M characters, 87 shards of 10M tokens each.
    

## Implementation Details (Verbatim)

"A custom Byte-Pair Encoding (BPE) tokenizer was trained with the vocabulary size of 16,384 using the SentencePiece library. The tokenizer was trained on an input sample of 8 million characters, with a maximum sentence length of 8192 characters and a character coverage of 0.9995. This tokenizer was then used to convert the full dataset into tokenized shards stored as NumPy files. The entire corpus was structured into 87 shards, each containing approximately 10 million tokens, enabling efficient loading during model training."

## Conclusion

Developing robust NLP systems for Nepali requires addressing unique linguistic complexities, building high-quality datasets, and designing custom tools (tokenizers, stemmers, lemmatizers) that respect the structure of Devanagari script. There is significant progress, but key gaps remain in tokenization, embedding, and attention mechanisms, especially for handling agglutinative morphology, SOV order, and complex ligatures.

