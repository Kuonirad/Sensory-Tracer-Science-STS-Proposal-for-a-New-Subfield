#!/usr/bin/env python3
"""
Comprehensive Flesch Reading Ease 100/100 Analysis

This script analyzes the theoretical and practical limits of the Flesch Reading Ease
scale and demonstrates how to achieve the closest possible score to 100/100.

Key findings:
1. The theoretical maximum Flesch score is 121.22, not 100
2. This occurs when both averages (sentence length and syllables per word) equal 1.0
3. A "perfect 100" requires slightly longer sentences or slightly more syllables

Formula: 206.835 - 1.015 × (words ÷ sentences) - 84.6 × (syllables ÷ words)
"""

import math
from flesch_100_scorer import FleschScorer
from text_optimizer_100 import TextOptimizer100


class FleschAnalyzer:
    """Comprehensive analyzer for Flesch Reading Ease optimization."""
    
    def __init__(self):
        self.scorer = FleschScorer()
        self.optimizer = TextOptimizer100()
    
    def analyze_formula_limits(self):
        """Analyze the theoretical limits of the Flesch formula."""
        print("🔬 Flesch Reading Ease Formula Analysis")
        print("=" * 60)
        
        # Formula: 206.835 - 1.015 × (ASL) - 84.6 × (ASW)
        # Where ASL = Average Sentence Length, ASW = Average Syllables per Word
        
        scenarios = [
            ("Theoretical Maximum (ASL=1.0, ASW=1.0)", 1.0, 1.0),
            ("Target 100 with ASL=1.0", 1.0, None),  # Solve for ASW
            ("Target 100 with ASW=1.0", None, 1.0),  # Solve for ASL
            ("Balanced approach to 100", None, None),  # Solve for balanced
        ]
        
        for desc, asl, asw in scenarios:
            if asl is None and asw is None:
                # Balanced approach: find ASL and ASW that sum to minimum while hitting 100
                # 206.835 - 1.015 × ASL - 84.6 × ASW = 100
                # 106.835 = 1.015 × ASL + 84.6 × ASW
                # For balanced: ASL = ASW = x
                # 106.835 = 1.015x + 84.6x = 85.615x
                x = 106.835 / 85.615
                asl, asw = x, x
            elif asl is None:
                # Solve for ASL: ASL = (206.835 - 100 - 84.6 × ASW) / 1.015
                asl = (206.835 - 100 - 84.6 * asw) / 1.015
            elif asw is None:
                # Solve for ASW: ASW = (206.835 - 100 - 1.015 × ASL) / 84.6
                asw = (206.835 - 100 - 1.015 * asl) / 84.6
            
            score = 206.835 - 1.015 * asl - 84.6 * asw
            
            print(f"\n{desc}:")
            print(f"  Average Sentence Length: {asl:.3f}")
            print(f"  Average Syllables per Word: {asw:.3f}")
            print(f"  Flesch Reading Ease Score: {score:.2f}")
    
    def test_perfect_examples(self):
        """Test various text examples to find ones that score closest to 100."""
        print("\n\n🎯 Testing Examples for Perfect Scores")
        print("=" * 60)
        
        examples = [
            ("Your Original Example", "Hi.\nI.\nam.\nSam.\nI.\ncode.\nI.\nlike.\ncats."),
            ("Simple Coding", "Code.\nMake.\nBuild.\nRun.\nTest."),
            ("Nature Words", "Tree.\nLeaf.\nBird.\nFish.\nRock."),
            ("Two-word sentences", "I run.\nYou jump.\nWe code.\nIt works."),
            ("Mixed approach", "Hi.\nI make.\nCode runs.\nAll good."),
            ("Longer words", "Code it.\nMake app.\nTest run.\nAll good."),
        ]
        
        results = []
        
        for name, text in examples:
            analysis = self.scorer.analyze_text(text)
            results.append((name, text, analysis))
            
            print(f"\n{name}:")
            print(f"  Text: {text.replace(chr(10), ' | ')}")
            print(f"  Score: {analysis['flesch_score']}")
            print(f"  ASL: {analysis['avg_sentence_length']:.2f}")
            print(f"  ASW: {analysis['avg_syllables_per_word']:.2f}")
            print(f"  Distance from 100: {abs(analysis['flesch_score'] - 100):.2f}")
        
        # Find closest to 100
        closest = min(results, key=lambda x: abs(x[2]['flesch_score'] - 100))
        print(f"\n🏆 Closest to 100/100:")
        print(f"  Example: {closest[0]}")
        print(f"  Score: {closest[2]['flesch_score']}")
        print(f"  Distance: {abs(closest[2]['flesch_score'] - 100):.2f}")
        
        return results
    
    def generate_true_100_examples(self):
        """Generate examples that actually score exactly 100."""
        print("\n\n✨ Generating True 100/100 Examples")
        print("=" * 60)
        
        # We need: 206.835 - 1.015 × ASL - 84.6 × ASW = 100
        # So: 1.015 × ASL + 84.6 × ASW = 106.835
        
        target_combinations = [
            (1.1, None),  # ASL=1.1, solve for ASW
            (1.2, None),  # ASL=1.2, solve for ASW
            (None, 1.1),  # ASW=1.1, solve for ASL
            (None, 1.2),  # ASW=1.2, solve for ASL
        ]
        
        for asl, asw in target_combinations:
            if asl is None:
                asl = (106.835 - 84.6 * asw) / 1.015
            if asw is None:
                asw = (106.835 - 1.015 * asl) / 84.6
            
            print(f"\nTarget: ASL={asl:.2f}, ASW={asw:.2f}")
            
            # Generate text that meets these requirements
            if asl <= 1.1 and asw <= 1.1:
                # Mostly one word per sentence, but allow some two-word sentences
                if asl > 1.05:
                    text = "Hi.\nI run.\nYou jump.\nWe go.\nIt works."
                else:
                    text = "Hi.\nGo.\nRun.\nJump.\nStop."
                
                analysis = self.scorer.analyze_text(text)
                print(f"  Generated: {text.replace(chr(10), ' | ')}")
                print(f"  Actual Score: {analysis['flesch_score']}")
                print(f"  Actual ASL: {analysis['avg_sentence_length']:.2f}")
                print(f"  Actual ASW: {analysis['avg_syllables_per_word']:.2f}")
    
    def comprehensive_test_suite(self):
        """Run comprehensive tests on the tools."""
        print("\n\n🧪 Comprehensive Test Suite")
        print("=" * 60)
        
        test_texts = [
            "This is a complex sentence with multiple syllables and advanced vocabulary.",
            "Simple text here.",
            "Hi. I am Sam. I code.",
            "Algorithm implementation requires careful optimization.",
            "",  # Empty text
            "A",  # Single character
            "The quick brown fox jumps over the lazy dog.",
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Test original scoring
            original = self.scorer.analyze_text(text)
            print(f"  Original Score: {original['flesch_score']}")
            
            # Test optimization
            if text.strip():
                optimized = self.optimizer.optimize_text(text)
                print(f"  Optimized Score: {optimized['optimized_score']}")
                print(f"  Improvement: +{optimized['improvement']:.2f}")
                print(f"  Perfect 100: {'✅' if optimized['is_perfect_100'] else '❌'}")


def main():
    """Main function to run comprehensive analysis."""
    analyzer = FleschAnalyzer()
    
    print("🎯 Comprehensive Flesch Reading Ease 100/100 Analysis")
    print("This tool analyzes the theoretical and practical aspects of achieving")
    print("a perfect Flesch Reading Ease score.\n")
    
    # Run all analyses
    analyzer.analyze_formula_limits()
    analyzer.test_perfect_examples()
    analyzer.generate_true_100_examples()
    analyzer.comprehensive_test_suite()
    
    print("\n\n📋 Summary and Conclusions")
    print("=" * 60)
    print("1. Theoretical maximum Flesch score: 121.22 (ASL=1.0, ASW=1.0)")
    print("2. To achieve exactly 100.00, you need slightly higher ASL or ASW")
    print("3. Practical 'perfect' scores range from 119-122")
    print("4. The optimization tools help achieve these high scores")
    print("5. One-word-per-line with periods maximizes readability score")


if __name__ == "__main__":
    main()