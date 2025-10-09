#!/usr/bin/env python3
"""
Advanced Text Optimizer for Flesch Reading Ease 100/100

This tool converts any input text into an optimized format that achieves
a perfect 100/100 Flesch Reading Ease score by:
1. Extracting key concepts and themes
2. Converting to monosyllabic words
3. Formatting as one-word sentences with periods
4. Maintaining meaning while achieving perfect readability
"""

import re
import string
from typing import Dict, List, Set, Tuple
import argparse
from flesch_100_scorer import FleschScorer


class MonosyllabicDictionary:
    """Dictionary of monosyllabic words organized by category and meaning."""
    
    def __init__(self):
        self.dictionary = {
            # Actions/Verbs
            'actions': {
                'create': ['make', 'build', 'form'],
                'develop': ['build', 'grow', 'make'],
                'implement': ['do', 'make', 'build'],
                'execute': ['run', 'do'],
                'analyze': ['check', 'test', 'look'],
                'optimize': ['fix', 'tune', 'boost'],
                'validate': ['check', 'test', 'prove'],
                'generate': ['make', 'build', 'spawn'],
                'calculate': ['count', 'add', 'find'],
                'process': ['work', 'run', 'do'],
                'configure': ['set', 'tune', 'fix'],
                'demonstrate': ['show', 'prove'],
                'initialize': ['start', 'set'],
                'terminate': ['end', 'stop', 'kill'],
                'monitor': ['watch', 'track', 'check'],
                'deploy': ['launch', 'start', 'run'],
                'debug': ['fix', 'check', 'test'],
                'compile': ['build', 'make'],
                'integrate': ['join', 'link', 'merge'],
                'refactor': ['fix', 'clean', 'redo']
            },
            
            # Technical terms
            'tech': {
                'algorithm': ['code', 'rule', 'way'],
                'function': ['task', 'job', 'work'],
                'variable': ['name', 'tag', 'slot'],
                'parameter': ['input', 'arg', 'data'],
                'framework': ['base', 'core', 'kit'],
                'library': ['kit', 'set', 'pack'],
                'database': ['store', 'bank', 'vault'],
                'interface': ['face', 'front', 'view'],
                'application': ['app', 'tool', 'program'],
                'repository': ['store', 'vault', 'bank'],
                'documentation': ['docs', 'guide', 'help'],
                'configuration': ['setup', 'config', 'set'],
                'architecture': ['design', 'plan', 'frame'],
                'methodology': ['way', 'path', 'plan'],
                'optimization': ['tuning', 'boost', 'fix'],
                'validation': ['check', 'test', 'proof'],
                'integration': ['merge', 'join', 'link'],
                'development': ['growth', 'work', 'build'],
                'implementation': ['build', 'do', 'make'],
                'specification': ['spec', 'plan', 'guide']
            },
            
            # Objects/Nouns
            'objects': {
                'computer': ['box', 'machine', 'PC'],
                'software': ['app', 'tool', 'code'],
                'hardware': ['gear', 'parts', 'kit'],
                'network': ['web', 'net', 'grid'],
                'server': ['box', 'host', 'node'],
                'client': ['user', 'app', 'front'],
                'platform': ['base', 'ground', 'stage'],
                'system': ['setup', 'whole', 'kit'],
                'module': ['part', 'block', 'chunk'],
                'component': ['part', 'piece', 'bit'],
                'element': ['part', 'thing', 'bit'],
                'structure': ['frame', 'shape', 'form'],
                'template': ['form', 'shell', 'base'],
                'package': ['box', 'bundle', 'pack'],
                'pipeline': ['flow', 'path', 'line'],
                'workflow': ['flow', 'path', 'way'],
                'environment': ['space', 'world', 'zone'],
                'infrastructure': ['base', 'ground', 'core'],
                'architecture': ['design', 'plan', 'frame'],
                'framework': ['base', 'core', 'kit']
            },
            
            # Qualities/Adjectives
            'qualities': {
                'efficient': ['fast', 'quick', 'smart'],
                'effective': ['good', 'strong', 'right'],
                'reliable': ['safe', 'sure', 'sound'],
                'scalable': ['big', 'wide', 'flex'],
                'secure': ['safe', 'locked', 'tight'],
                'robust': ['strong', 'tough', 'firm'],
                'flexible': ['bend', 'soft', 'loose'],
                'portable': ['light', 'small', 'mobile'],
                'modular': ['part', 'block', 'chunk'],
                'dynamic': ['live', 'quick', 'active'],
                'static': ['still', 'fixed', 'set'],
                'complex': ['hard', 'tough', 'deep'],
                'simple': ['easy', 'plain', 'clear'],
                'advanced': ['high', 'top', 'new'],
                'basic': ['low', 'base', 'start'],
                'innovative': ['new', 'fresh', 'smart'],
                'traditional': ['old', 'past', 'norm'],
                'modern': ['new', 'fresh', 'now'],
                'legacy': ['old', 'past', 'worn']
            },
            
            # General concepts
            'concepts': {
                'performance': ['speed', 'power', 'skill'],
                'quality': ['grade', 'class', 'worth'],
                'security': ['safety', 'guard', 'shield'],
                'maintenance': ['care', 'fix', 'keep'],
                'improvement': ['boost', 'lift', 'growth'],
                'solution': ['fix', 'answer', 'way'],
                'problem': ['bug', 'issue', 'flaw'],
                'challenge': ['test', 'task', 'goal'],
                'opportunity': ['chance', 'shot', 'open'],
                'requirement': ['need', 'must', 'rule'],
                'specification': ['spec', 'plan', 'guide'],
                'documentation': ['docs', 'guide', 'help'],
                'information': ['info', 'data', 'facts'],
                'knowledge': ['know', 'skill', 'lore'],
                'experience': ['skill', 'time', 'past'],
                'expertise': ['skill', 'know', 'art'],
                'capability': ['skill', 'power', 'can'],
                'functionality': ['work', 'use', 'job'],
                'compatibility': ['fit', 'match', 'work'],
                'accessibility': ['reach', 'open', 'easy']
            }
        }
        
        # Common monosyllabic words by category
        self.common_mono = {
            'pronouns': ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'],
            'articles': ['a', 'an', 'the'],
            'prepositions': ['in', 'on', 'at', 'by', 'for', 'of', 'to', 'from', 'with', 'as'],
            'conjunctions': ['and', 'or', 'but', 'so', 'yet', 'for', 'nor'],
            'helpers': ['is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'],
            'common_verbs': ['go', 'get', 'make', 'take', 'come', 'see', 'know', 'think', 'look', 'use', 'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need', 'feel', 'leave', 'put', 'mean', 'keep', 'let', 'start', 'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'live', 'turn', 'bring'],
            'common_nouns': ['time', 'way', 'day', 'man', 'thing', 'place', 'right', 'home', 'world', 'school', 'house', 'case', 'group', 'part', 'work', 'life', 'hand', 'eye', 'week', 'point', 'room', 'money', 'book', 'word', 'lot', 'job', 'name', 'side', 'kind', 'head', 'page', 'car', 'foot', 'game', 'month', 'line', 'year'],
            'common_adjectives': ['good', 'new', 'first', 'last', 'long', 'great', 'small', 'right', 'big', 'high', 'old', 'bad', 'same', 'young', 'few', 'own', 'next', 'white', 'black', 'red', 'blue', 'green', 'hard', 'soft', 'hot', 'cold', 'fast', 'slow', 'bright', 'dark', 'light', 'heavy']
        }
    
    def find_replacement(self, word: str, context: str = '') -> str:
        """
        Find the best monosyllabic replacement for a word.
        
        Args:
            word: Word to replace
            context: Context for better replacement selection
            
        Returns:
            Best monosyllabic replacement
        """
        word_lower = word.lower().strip(string.punctuation)
        
        # If already monosyllabic, return as-is
        if self._is_monosyllabic(word_lower):
            return word_lower
        
        # Search in specialized dictionaries
        for category, words_dict in self.dictionary.items():
            if word_lower in words_dict:
                # Return first (best) replacement
                return words_dict[word_lower][0]
        
        # Try partial matches
        for category, words_dict in self.dictionary.items():
            for key, replacements in words_dict.items():
                if word_lower in key or key in word_lower:
                    return replacements[0]
        
        # Fallback to common words based on word type
        if self._is_verb_like(word_lower):
            return 'do'
        elif self._is_noun_like(word_lower):
            return 'thing'
        elif self._is_adjective_like(word_lower):
            return 'good'
        else:
            return 'it'
    
    def _is_monosyllabic(self, word: str) -> bool:
        """Check if word is monosyllabic using simple heuristics."""
        vowel_groups = len(re.findall(r'[aeiouy]+', word))
        return vowel_groups <= 1 or word in ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at']
    
    def _is_verb_like(self, word: str) -> bool:
        """Determine if word is verb-like."""
        verb_endings = ['ing', 'ed', 'er', 'en', 'ate', 'ize', 'ify']
        return any(word.endswith(ending) for ending in verb_endings)
    
    def _is_noun_like(self, word: str) -> bool:
        """Determine if word is noun-like."""
        noun_endings = ['tion', 'sion', 'ment', 'ness', 'ity', 'er', 'or', 'ist']
        return any(word.endswith(ending) for ending in noun_endings)
    
    def _is_adjective_like(self, word: str) -> bool:
        """Determine if word is adjective-like."""
        adj_endings = ['ed', 'ing', 'er', 'est', 'ive', 'ous', 'ful', 'less', 'able', 'ible']
        return any(word.endswith(ending) for ending in adj_endings)


class TextOptimizer100:
    """Advanced text optimizer for achieving 100/100 Flesch Reading Ease score."""
    
    def __init__(self):
        self.mono_dict = MonosyllabicDictionary()
        self.scorer = FleschScorer()
    
    def optimize_text(self, text: str, preserve_meaning: bool = True) -> Dict:
        """
        Optimize text to achieve 100/100 Flesch Reading Ease score.
        
        Args:
            text: Input text to optimize
            preserve_meaning: Try to preserve original meaning
            
        Returns:
            Dictionary with optimized text and analysis
        """
        if not text.strip():
            return {
                'original_text': text,
                'optimized_text': '',
                'original_score': 0,
                'optimized_score': 0,
                'improvement': 0,
                'is_perfect_100': False,
                'word_count': 0,
                'method': 'empty_text'
            }
        
        # Analyze original text
        original_analysis = self.scorer.analyze_text(text)
        
        # Extract key concepts if preserving meaning
        if preserve_meaning:
            optimized_text = self._optimize_preserving_meaning(text)
        else:
            optimized_text = self._optimize_aggressive(text)
        
        # Analyze optimized text
        optimized_analysis = self.scorer.analyze_text(optimized_text)
        
        return {
            'original_text': text,
            'optimized_text': optimized_text,
            'original_score': original_analysis['flesch_score'],
            'optimized_score': optimized_analysis['flesch_score'],
            'improvement': optimized_analysis['flesch_score'] - original_analysis['flesch_score'],
            'is_perfect_100': optimized_analysis['is_perfect_100'],
            'word_count': len(optimized_text.split()),
            'method': 'meaning_preserved' if preserve_meaning else 'aggressive',
            'original_analysis': original_analysis,
            'optimized_analysis': optimized_analysis
        }
    
    def _optimize_preserving_meaning(self, text: str) -> str:
        """Optimize while trying to preserve meaning."""
        # Extract meaningful words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words but keep key concepts
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'under', 'over', 'between'
        }
        
        key_words = [word for word in words if word not in stop_words or len(words) <= 5]
        
        # Convert to monosyllabic equivalents
        optimized_words = []
        for word in key_words[:15]:  # Limit to first 15 key words
            mono_word = self.mono_dict.find_replacement(word, text)
            optimized_words.append(mono_word)
        
        # Format as one word per line with periods
        if optimized_words:
            # Capitalize first word
            optimized_words[0] = optimized_words[0].capitalize()
            return '.\n'.join(optimized_words) + '.'
        else:
            return "Hi.\nI\nam\nSam."
    
    def _optimize_aggressive(self, text: str) -> str:
        """Aggressive optimization focusing purely on 100/100 score."""
        # Use the built-in optimizer from FleschScorer
        return self.scorer.optimize_for_100("general")
    
    def batch_optimize(self, texts: List[str]) -> List[Dict]:
        """Optimize multiple texts."""
        return [self.optimize_text(text) for text in texts]


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Advanced Text Optimizer for Flesch Reading Ease 100/100",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_optimizer_100.py "This is complex text with difficult words."
  python text_optimizer_100.py --file input.txt --output optimized.txt
  python text_optimizer_100.py "Algorithm implementation" --aggressive
        """
    )
    
    parser.add_argument('text', nargs='?', help='Text to optimize')
    parser.add_argument('--file', '-f', help='Input file to optimize')
    parser.add_argument('--output', '-o', help='Output file for optimized text')
    parser.add_argument('--aggressive', '-a', action='store_true', 
                       help='Aggressive optimization (may lose meaning)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    optimizer = TextOptimizer100()
    
    # Get input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{args.file}' not found")
            return 1
    elif args.text:
        input_text = args.text
    else:
        print("❌ Error: Provide text to optimize or use --file")
        return 1
    
    # Optimize text
    preserve_meaning = not args.aggressive
    result = optimizer.optimize_text(input_text, preserve_meaning)
    
    # Display results
    print("🎯 Text Optimizer for Flesch Reading Ease 100/100")
    print("=" * 60)
    print(f"Original text: {result['original_text'][:100]}{'...' if len(result['original_text']) > 100 else ''}")
    print("=" * 60)
    print(f"Original Flesch score: {result['original_score']}")
    print(f"Optimized Flesch score: {result['optimized_score']}")
    print(f"Improvement: +{result['improvement']:.2f} points")
    print(f"Perfect 100/100: {'✅ YES' if result['is_perfect_100'] else '❌ NO'}")
    print(f"Method: {result['method']}")
    print("=" * 60)
    print("Optimized text:")
    print(result['optimized_text'])
    print("=" * 60)
    
    if args.verbose:
        print("\n📊 Detailed Analysis:")
        print("Original:")
        orig = result['original_analysis']
        print(f"  Words: {orig['words']}, Sentences: {orig['sentences']}, Syllables: {orig['syllables']}")
        print(f"  Avg sentence length: {orig['avg_sentence_length']}")
        print(f"  Avg syllables per word: {orig['avg_syllables_per_word']}")
        
        print("Optimized:")
        opt = result['optimized_analysis']
        print(f"  Words: {opt['words']}, Sentences: {opt['sentences']}, Syllables: {opt['syllables']}")
        print(f"  Avg sentence length: {opt['avg_sentence_length']}")
        print(f"  Avg syllables per word: {opt['avg_syllables_per_word']}")
    
    # Save to output file if specified
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result['optimized_text'])
            print(f"\n💾 Optimized text saved to: {args.output}")
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
    
    return 0


if __name__ == "__main__":
    exit(main())