#!/usr/bin/env python3
"""
Detailed readability analysis to identify specific problems in README.md
"""

import re
import textstat
from typing import List, Dict

def analyze_readme_readability(file_path: str):
    """Analyze specific readability issues in README"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Analysis results
    print("🔍 DETAILED READABILITY ANALYSIS")
    print("=" * 50)
    
    # Overall metrics
    flesch_score = textstat.flesch_reading_ease(content)
    grade_level = textstat.flesch_kincaid_grade(content)
    
    print(f"📊 Flesch Reading Ease: {flesch_score:.1f}")
    print(f"📚 Grade Level: {grade_level:.1f}")
    print(f"🎯 Target: 60+ (easy) and grade 8-10\n")
    
    # Sentence analysis
    print("📝 SENTENCE ANALYSIS:")
    print("-" * 30)
    
    long_sentences = []
    word_counts = []
    
    for i, sentence in enumerate(sentences):
        words = len(sentence.split())
        word_counts.append(words)
        
        if words > 20:  # Very long sentences
            long_sentences.append((i+1, sentence[:80] + "...", words))
    
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    
    print(f"📈 Average words per sentence: {avg_words:.1f}")
    print(f"🎯 Target: 15-20 words per sentence")
    print(f"❌ Long sentences (>20 words): {len(long_sentences)}")
    
    if long_sentences:
        print("\n🔴 PROBLEM SENTENCES (>20 words):")
        for num, sentence, word_count in long_sentences[:5]:
            print(f"  {num:3d}. [{word_count:2d}w] {sentence}")
    
    # Complex word analysis
    print(f"\n🔤 WORD COMPLEXITY:")
    print("-" * 30)
    
    words = re.findall(r'\b\w+\b', content.lower())
    long_words = [w for w in words if len(w) > 6]
    technical_words = [w for w in words if w in [
        'biocompatible', 'thermodynamic', 'heisenberg', 'quantum', 
        'biochemical', 'neurological', 'toxicity', 'implementation',
        'validation', 'compatibility', 'comprehensive', 'regulatory'
    ]]
    
    print(f"📊 Long words (>6 chars): {len(long_words)} / {len(words)} ({len(long_words)/len(words)*100:.1f}%)")
    print(f"🎯 Target: <20% long words")
    print(f"🧬 Technical terms: {len(technical_words)} occurrences")
    
    # Suggestions
    print(f"\n💡 IMPROVEMENT PRIORITIES:")
    print("-" * 30)
    
    if avg_words > 18:
        print("1. 📝 Break long sentences into 2-3 shorter ones")
    if len(long_words)/len(words) > 0.2:
        print("2. 🔤 Replace complex words with simpler alternatives")
    if flesch_score < 50:
        print("3. 📖 Improve overall readability structure")
    
    print("\n🔧 SPECIFIC FIXES NEEDED:")
    print("-" * 30)
    print("• Convert passive voice to active voice")
    print("• Use bullet points instead of long paragraphs") 
    print("• Add more white space between sections")
    print("• Simplify technical explanations")
    print("• Use shorter, punchier sentences")

if __name__ == "__main__":
    analyze_readme_readability("README.md")