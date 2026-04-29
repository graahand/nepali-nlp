import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from matplotlib import font_manager

# Explicitly add the Noto Sans Devanagari font
font_path = '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf'
font_manager.fontManager.addfont(font_path)
devanagari_prop = font_manager.FontProperties(fname=font_path)

# Set plotting style for academic presentation
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# Keep the global font as standard for Latin/English characters
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False 

# Directory to save visualizations
SAVE_DIR = "plots"
os.makedirs(SAVE_DIR, exist_ok=True)

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# ---------------------------------------------------------
# 1. Corpus Size Metrics
# ---------------------------------------------------------
def plot_corpus_size():
    labels = ['Total Documents', 'Sentences', 'Words (Tokens)', 'Characters']
    counts = [5176975, 84890912, 1221814455, 8344616414]
    
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=labels, y=counts, palette="Blues_d")
    ax.set_yscale('log')
    plt.title('1. Corpus Size Metrics (Log Scale)', pad=15)
    plt.ylabel('Count (Log Scale)')
    save_plot('1_corpus_size_metrics.png')

# ---------------------------------------------------------
# 2. Vocabulary & Typology
# ---------------------------------------------------------
def plot_vocabulary():
    labels = ['Total Unique Types', 'Hapax Legomena']
    counts = [5517510, 2645392]
    
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=counts, palette="Purples_d")
    plt.title('2. Unique Vocabulary and Hapax Legomena', pad=15)
    plt.ylabel('Count (Millions)')
    save_plot('2_vocabulary_typology.png')

# ---------------------------------------------------------
# 3. Source / Domain Distribution
# ---------------------------------------------------------
def plot_sources():
    sources = [
        "ratopati.com", "gorkhapatraonline.com", "ekantipur.com", "nepalkhabar.com",
        "annapurnapost.com", "imagekhabar.com", "reportersnepal.com", "newsofnepal.com",
        "lokpath.com", "setopati.com", "kendrabindu.com", "makalukhabar.com",
        "drishtinews.com", "hamrakura.com", "nepallive.com"
    ]
    counts = [
        308638, 279640, 215317, 195445, 183946, 181443, 170573, 156199,
        150252, 138866, 137212, 123538, 118406, 118239, 115953
    ]
    
    df = pd.DataFrame({'Source': sources, 'Documents': counts})
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Documents', y='Source', data=df, palette="crest")
    plt.title('3. Source / Domain Distribution (Top 15)', pad=15)
    plt.xlabel('Number of Documents')
    save_plot('3_source_distribution.png')

# ---------------------------------------------------------
# 4. Length Distributions
# ---------------------------------------------------------
def plot_length_distributions():
    metrics = ['Mean', 'Median', 'Q1', 'Q3']
    doc_sents = [16.4, 10, 6, 19]
    doc_words = [236.01, 161, 94, 276]
    sent_words = [14.39, 13, 9, 18]
    
    df = pd.DataFrame({
        'Metric': metrics * 3,
        'Value': doc_sents + doc_words + sent_words,
        'Category': ['Document (Sentences)']*4 + ['Document (Words)']*4 + ['Sentence (Words)']*4
    })
    
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x='Category', y='Value', hue='Metric', palette="Set2")
    plt.title('4. Length Distributions (Central Tendencies)', pad=15)
    plt.ylabel('Counts')
    plt.yscale('log')
    save_plot('4_length_distributions.png')

# ---------------------------------------------------------
# 5 & 6. Character & Digit Scripts (Devanagari vs Latin)
# ---------------------------------------------------------
def plot_script_ratios():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 5. Characters
    char_labels = ['Devanagari\n(6.99B)', 'Other (Punct/Sym)\n(1.35B)']
    char_sizes = [6990410258, 1354206156]
    axes[0].pie(char_sizes, labels=char_labels, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#9E9E9E'])
    axes[0].set_title('5. Devanagari vs Other Characters')
    
    # 6. Digits
    digit_labels = ['Devanagari Digits\n(81.6M)', 'ASCII Digits\n(0)']
    digit_sizes = [81612017, 0] # Need a small arbitrary value for pie to not break if 0, but 0 is fine natively in matplotlib 
    # Just draw one wedge if ASCII is genuinely 0
    axes[1].pie([100], labels=['Devanagari Digits (100%)'], colors=['#FF9800'])
    axes[1].set_title('6. Digit Distribution')
    
    save_plot('5_6_script_ratios.png')

# ---------------------------------------------------------
# 7 & 8. Typology: Halanta & Suffixes
# ---------------------------------------------------------
def plot_typology():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Suffix vs non-Suffix
    suffix_sizes = [337156050, 1221814455 - 337156050]
    axes[0].pie(suffix_sizes, labels=['Suffix-bearing\n(27.6%)', 'Non Suffix-bearing\n(72.4%)'], 
                autopct='%1.1f%%', colors=['#F44336', '#B0BEC5'])
    axes[0].set_title('Suffix-bearing Words Ratio')
    
    # Suffix distributions (Top 10)
    top_suffixes = ['को', 'मा', 'ले', 'का', 'लाई', 'बाट', 'की', 'सँग', 'हरु', 'हरू']
    top_counts = [113055535, 68330516, 55472127, 53038703, 18867610, 8496332, 4527706, 3040520, 2353704, 2199232]
    
    ax_bar = sns.barplot(x=top_counts, y=top_suffixes, ax=axes[1], palette="flare")
    axes[1].set_title('Top 10 Suffixes')
    axes[1].set_xlabel('Frequency')
    
    # Safely apply Devanagari Font exclusively to Nepali text object strings on y-axis
    for label in ax_bar.get_yticklabels():
        label.set_fontproperties(devanagari_prop)
    
    plt.suptitle('7 & 8. Typology (Suffixes & Fragmentation)', y=1.05)
    save_plot('7_8_typology_suffixes.png')

# ---------------------------------------------------------
# 9. Noise Rates
# ---------------------------------------------------------
def plot_noise():
    labels = ['Phone Numbers', 'HTML Remnants']
    counts = [12988, 18]
    
    plt.figure(figsize=(6, 4))
    ax = sns.barplot(x=labels, y=counts, palette="Reds_d")
    ax.set_yscale('log')
    plt.title('9. Noise Rates (Log Scale)', pad=15)
    plt.ylabel('Occurrences')
    save_plot('9_noise_rates.png')

# ---------------------------------------------------------
# 10. Top 20 Most Frequent Words
# ---------------------------------------------------------
def plot_top_words():
    # Only picking the top 20 for readability in a single plot
    words = ['छ', 'र', 'पनि', 'भएको', 'छन्', 'गरेको', 'लागि', 'हो', 'तथा', 'भने',
             'गर्न', 'गर्ने', 'थियो', 'उनले', 'रहेको', 'एक', 'हुने', 'यो', 'गरेका', 'नै']
    counts = [23476790, 21675422, 10790404, 9073826, 8677935, 7153683, 6773368, 6171993, 
              5796179, 5796174, 5475477, 5450547, 5251727, 4497549, 4145280, 3817349, 
              3639622, 3463896, 3402255, 3367739]
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=counts, y=words, palette="viridis")
    plt.title('10. Top 20 Most Frequent Words', pad=15)
    plt.xlabel('Frequency (Ten Millions)')
        
    for label in ax.get_yticklabels():
        label.set_fontproperties(devanagari_prop)
        label.set_fontsize(14)
        
    save_plot('10_top_frequent_words.png')

if __name__ == "__main__":
    print("Generating Visualizations...")
    plot_corpus_size()
    plot_vocabulary()
    plot_sources()
    plot_length_distributions()
    plot_script_ratios()
    plot_typology()
    plot_noise()
    plot_top_words()
    print(f"All visualizations have been successfully saved to {os.path.abspath(SAVE_DIR)}/")
    
