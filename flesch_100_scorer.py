#!/usr/bin/env python3
"""
Flesch Reading Ease 100/100 Scorer and Optimizer

This tool implements the exact Flesch Reading Ease formula and provides utilities
to achieve a perfect 100/100 score by following specific text formatting rules.

Formula: 206.835 - 1.015 × (words ÷ sentences) - 84.6 × (syllables ÷ words)

To achieve 100/100:
- Average sentence length must be as close to 1 as possible (ideally 1)
- Average syllables per word must be as close to 1 as possible (ideally 1)
"""

import re
import string
from typing import Dict, List, Tuple
import argparse
import sys


class SyllableCounter:
    """Advanced syllable counter for accurate scoring."""
    
    def __init__(self):
        # Common single-syllable endings that might be miscounted
        self.single_syllable_endings = {
            'ced', 'ces', 'led', 'les', 'red', 'res', 'sed', 'ses',
            'ted', 'tes', 'ved', 'ves', 'wed', 'wes', 'yed', 'yes'
        }
        
        # Vowel combinations that count as single syllables
        self.single_vowel_combos = {
            'ai', 'au', 'ay', 'ea', 'ee', 'ei', 'eu', 'ey', 
            'ie', 'oa', 'oe', 'oo', 'ou', 'ow', 'oy', 'ue', 'ui'
        }
    
    def count_syllables(self, word: str) -> int:
        """
        Count syllables in a word using improved algorithm.
        
        Args:
            word: Input word (string)
            
        Returns:
            Number of syllables (int)
        """
        if not word:
            return 0
            
        word = word.lower().strip(string.punctuation)
        if not word:
            return 0
            
        # Special cases for common monosyllabic words
        monosyllabic = {
            'a', 'an', 'and', 'as', 'at', 'be', 'by', 'for', 'he', 'i', 'in', 'is', 'it',
            'my', 'no', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'we', 'you',
            'cat', 'dog', 'run', 'big', 'red', 'fox', 'hop', 'sun', 'sky', 'sea',
            'hi', 'am', 'code', 'like', 'cats', 'sam', 'get', 'go', 'see', 'do',
            'make', 'take', 'come', 'some', 'time', 'here', 'there', 'where'
        }
        
        if word in monosyllabic:
            return 1
            
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for i, char in enumerate(word):
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e' at the end
        if word.endswith('e') and syllable_count > 1:
            if len(word) > 3 and word[-2] not in vowels:
                syllable_count -= 1
        
        # Handle special endings
        if len(word) > 3:
            ending = word[-3:]
            if ending in self.single_syllable_endings:
                syllable_count = max(1, syllable_count - 1)
        
        # Every word has at least one syllable
        return max(1, syllable_count)


class FleschScorer:
    """Flesch Reading Ease scorer with 100/100 optimization."""
    
    def __init__(self):
        self.syllable_counter = SyllableCounter()
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text and calculate Flesch Reading Ease score.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with detailed analysis results
        """
        if not text.strip():
            return {
                'flesch_score': 0,
                'words': 0,
                'sentences': 0,
                'syllables': 0,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0,
                'grade_level': 'N/A',
                'is_perfect_100': False,
                'suggestions': ['Text is empty']
            }
        
        # Count sentences (periods, exclamation marks, question marks)
        # For 100/100 score, we need to count each line ending with punctuation as a sentence
        sentences = len(re.findall(r'[.!?]+', text))
        if sentences == 0:
            sentences = 1  # At least one sentence if no punctuation
        
        # Count words (split by whitespace, filter empty)
        words = len([w for w in text.split() if w.strip()])
        
        # Count syllables
        word_list = re.findall(r'\b\w+\b', text.lower())
        total_syllables = sum(self.syllable_counter.count_syllables(word) for word in word_list)
        
        if words == 0:
            return {
                'flesch_score': 0,
                'words': words,
                'sentences': sentences,
                'syllables': total_syllables,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0,
                'grade_level': 'N/A',
                'is_perfect_100': False,
                'suggestions': ['No words found']
            }
        
        # Calculate averages
        avg_sentence_length = words / sentences
        avg_syllables_per_word = total_syllables / words
        
        # Flesch Reading Ease formula
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Determine grade level
        grade_level = self._get_grade_level(flesch_score)
        
        # Check if perfect 100
        is_perfect_100 = abs(flesch_score - 100) < 0.1
        
        # Generate suggestions
        suggestions = self._generate_suggestions(avg_sentence_length, avg_syllables_per_word, flesch_score)
        
        return {
            'flesch_score': round(flesch_score, 2),
            'words': words,
            'sentences': sentences,
            'syllables': total_syllables,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'grade_level': grade_level,
            'is_perfect_100': is_perfect_100,
            'suggestions': suggestions
        }
    
    def _get_grade_level(self, score: float) -> str:
        """Convert Flesch score to grade level."""
        if score >= 90:
            return "5th grade"
        elif score >= 80:
            return "6th grade"
        elif score >= 70:
            return "7th grade"
        elif score >= 60:
            return "8th & 9th grade"
        elif score >= 50:
            return "10th to 12th grade"
        elif score >= 30:
            return "College level"
        else:
            return "Graduate level"
    
    def _generate_suggestions(self, avg_sent_len: float, avg_syll: float, score: float) -> List[str]:
        """Generate suggestions for improving the score."""
        suggestions = []
        
        if score < 100:
            if avg_sent_len > 1.1:
                suggestions.append(f"Reduce average sentence length from {avg_sent_len:.2f} to 1.0 (use one word per sentence)")
            
            if avg_syll > 1.1:
                suggestions.append(f"Reduce average syllables per word from {avg_syll:.2f} to 1.0 (use only monosyllabic words)")
            
            suggestions.append("End every line with a period to maximize sentence count")
            suggestions.append("Use only single-syllable words: cat, dog, run, big, red, etc.")
            suggestions.append("Format as one word per line with periods")
        
        if not suggestions:
            suggestions.append("Perfect! This text achieves 100/100 Flesch Reading Ease score!")
        
        return suggestions
    
    def optimize_for_100(self, concept: str = "coding") -> str:
        """
        Generate text optimized for 100/100 Flesch score.
        
        Args:
            concept: Theme/concept for the optimized text
            
        Returns:
            Optimized text that should score 100/100
        """
        # Monosyllabic word bank by category
        word_banks = {
            "coding": ["code", "make", "build", "run", "test", "fix", "git", "push", "pull", "merge", "debug", "app"],
            "nature": ["tree", "leaf", "bird", "fish", "rock", "sun", "moon", "star", "sea", "lake", "hill", "grass"],
            "animals": ["cat", "dog", "fox", "bear", "fish", "bird", "bee", "ant", "cow", "pig", "sheep", "goat"],
            "colors": ["red", "blue", "green", "black", "white", "pink", "gold", "gray", "brown", "tan"],
            "actions": ["run", "jump", "walk", "sit", "stand", "look", "see", "hear", "feel", "think", "know", "learn"],
            "general": ["hi", "am", "like", "get", "go", "do", "make", "take", "give", "have", "want", "need", "good", "bad", "big", "small"]
        }
        
        # Select appropriate word bank
        words = word_banks.get(concept, word_banks["general"])
        
        # Create optimized text (one word per line with periods)
        optimized_lines = []
        for i, word in enumerate(words[:10]):  # Use first 10 words
            optimized_lines.append(f"{word.title()}." if i == 0 else f"{word}.")
        
        return "\n".join(optimized_lines)


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Flesch Reading Ease 100/100 Scorer and Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flesch_100_scorer.py "Hi. I am Sam. I code. I like cats."
  python flesch_100_scorer.py --optimize coding
  python flesch_100_scorer.py --file input.txt
        """
    )
    
    parser.add_argument('text', nargs='?', help='Text to analyze')
    parser.add_argument('--file', '-f', help='File to analyze')
    parser.add_argument('--optimize', '-o', help='Generate optimized text for concept')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    scorer = FleschScorer()
    
    if args.optimize:
        print(f"🎯 Generating text optimized for 100/100 Flesch score (concept: {args.optimize})")
        print("=" * 60)
        optimized_text = scorer.optimize_for_100(args.optimize)
        print(optimized_text)
        print("=" * 60)
        
        # Analyze the optimized text
        result = scorer.analyze_text(optimized_text)
        print(f"📊 Analysis of optimized text:")
        print(f"Flesch Reading Ease Score: {result['flesch_score']}")
        print(f"Perfect 100/100: {'✅ YES' if result['is_perfect_100'] else '❌ NO'}")
        
        if args.verbose:
            print(f"\nDetailed Analysis:")
            print(f"Words: {result['words']}")
            print(f"Sentences: {result['sentences']}")
            print(f"Syllables: {result['syllables']}")
            print(f"Avg sentence length: {result['avg_sentence_length']}")
            print(f"Avg syllables per word: {result['avg_syllables_per_word']}")
        
        return
    
    # Get text to analyze
    text = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{args.file}' not found")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("❌ Error: Provide text to analyze or use --optimize")
        sys.exit(1)
    
    # Analyze text
    result = scorer.analyze_text(text)
    
    # Display results
    print("📊 Flesch Reading Ease Analysis")
    print("=" * 50)
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print("=" * 50)
    print(f"Flesch Reading Ease Score: {result['flesch_score']}")
    print(f"Grade Level: {result['grade_level']}")
    print(f"Perfect 100/100: {'✅ YES' if result['is_perfect_100'] else '❌ NO'}")
    
    if args.verbose or result['flesch_score'] < 95:
        print(f"\n📈 Detailed Metrics:")
        print(f"Words: {result['words']}")
        print(f"Sentences: {result['sentences']}")
        print(f"Syllables: {result['syllables']}")
        print(f"Average sentence length: {result['avg_sentence_length']}")
        print(f"Average syllables per word: {result['avg_syllables_per_word']}")
    
    if not result['is_perfect_100']:
        print(f"\n💡 Suggestions to reach 100/100:")
        for suggestion in result['suggestions']:
            print(f"   • {suggestion}")


if __name__ == "__main__":
    main()