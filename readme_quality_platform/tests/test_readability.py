"""
Test suite for readability analysis functionality.

Comprehensive tests covering all readability metrics including Flesch Reading Ease,
Flesch-Kincaid Grade Level, Gunning Fog, SMOG, Dale-Chall, and ARI calculations.
"""

import unittest
from readme_quality_platform.metrics.readability import ReadabilityAnalyzer
from readme_quality_platform.core.models import ReadabilityMetrics


class TestReadabilityAnalyzer(unittest.TestCase):
    """Test cases for ReadabilityAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ReadabilityAnalyzer()
        
        # Test texts with known characteristics
        self.simple_text = """
        This is a simple text. It has short sentences. 
        The words are easy to read. Most people can understand it.
        """
        
        self.complex_text = """
        The implementation of sophisticated algorithmic methodologies necessitates 
        comprehensive understanding of multidimensional computational frameworks, 
        particularly those involving probabilistic optimization techniques and 
        hierarchical data structures that facilitate efficient information retrieval 
        across heterogeneous distributed systems architecture.
        """
        
        self.mixed_text = """
        # Project Overview
        
        This project provides a comprehensive solution for analyzing README files.
        It uses advanced natural language processing techniques to evaluate
        documentation quality across multiple dimensions.
        
        ## Features
        
        - **Readability Analysis**: Implements multiple established formulas
        - **Structural Assessment**: Evaluates organization and completeness  
        - **Complexity Scoring**: Measures sophistication and richness
        - **Code Consistency**: Analyzes alignment with repository content
        
        The system employs sophisticated computational linguistics algorithms
        to provide actionable insights for improving documentation effectiveness.
        """
        
        self.empty_text = ""
        self.single_word = "Hello"
    
    def test_simple_text_analysis(self):
        """Test analysis of simple, readable text."""
        metrics = self.analyzer.analyze(self.simple_text)
        
        # Simple text should have high readability
        self.assertGreater(metrics.flesch_reading_ease, 70)
        self.assertLess(metrics.flesch_kincaid_grade, 8)
        self.assertGreater(metrics.word_count, 0)
        self.assertGreater(metrics.sentence_count, 0)
        self.assertIn(metrics.readability_consensus, ['very easy', 'easy', 'fairly easy'])
    
    def test_complex_text_analysis(self):
        """Test analysis of complex, difficult text.""" 
        metrics = self.analyzer.analyze(self.complex_text)
        
        # Complex text should have low readability
        self.assertLess(metrics.flesch_reading_ease, 50)
        self.assertGreater(metrics.flesch_kincaid_grade, 12)
        self.assertGreater(metrics.polysyllable_count, 5)
        self.assertIn(metrics.readability_consensus, ['difficult', 'very difficult'])
    
    def test_mixed_text_analysis(self):
        """Test analysis of mixed complexity text (typical README)."""
        metrics = self.analyzer.analyze(self.mixed_text)
        
        # Should be moderately readable
        self.assertGreater(metrics.flesch_reading_ease, 30)
        self.assertLess(metrics.flesch_reading_ease, 80)
        self.assertGreater(metrics.word_count, 50)
        self.assertGreater(metrics.sentence_count, 5)
        self.assertGreater(metrics.average_grade_level, 8)
        self.assertLess(metrics.average_grade_level, 16)
    
    def test_empty_text_handling(self):
        """Test handling of empty text."""
        metrics = self.analyzer.analyze(self.empty_text)
        
        self.assertEqual(metrics.word_count, 0)
        self.assertEqual(metrics.sentence_count, 0)
        self.assertEqual(metrics.flesch_reading_ease, 0)
    
    def test_single_word_handling(self):
        """Test handling of single word."""
        metrics = self.analyzer.analyze(self.single_word)
        
        self.assertEqual(metrics.word_count, 1)
        # Should handle gracefully without errors
        self.assertIsInstance(metrics.flesch_reading_ease, float)
    
    def test_flesch_reading_ease_calculation(self):
        """Test specific Flesch Reading Ease calculation."""
        # Known text with predictable metrics
        test_text = "The cat sat on the mat. It was a nice day."
        metrics = self.analyzer.analyze(test_text)
        
        # Should be in reasonable range
        self.assertGreater(metrics.flesch_reading_ease, 50)
        self.assertLess(metrics.flesch_reading_ease, 100)
    
    def test_syllable_counting(self):
        """Test syllable counting accuracy."""
        # Test words with known syllable counts
        test_cases = [
            ("hello", 2),
            ("cat", 1), 
            ("beautiful", 3),
            ("algorithm", 4),
            ("a", 1),
        ]
        
        for word, expected_syllables in test_cases:
            syllables = self.analyzer._syllables_in_word(word)
            self.assertGreaterEqual(syllables, 1)  # Minimum 1 syllable
            # Allow some tolerance for syllable counting algorithms
            self.assertLessEqual(abs(syllables - expected_syllables), 1)
    
    def test_polysyllable_counting(self):
        """Test polysyllable (3+ syllables) word counting."""
        words = ["cat", "hello", "beautiful", "algorithm", "sophisticated"]
        polysyllables = self.analyzer._count_polysyllables(words)
        
        # Should count words with 3+ syllables
        self.assertGreaterEqual(polysyllables, 2)  # "beautiful", "algorithm", "sophisticated"
    
    def test_dale_chall_scoring(self):
        """Test Dale-Chall readability scoring."""
        # Text with common words should score better
        common_text = "The cat and dog are friends. They play together every day."
        complex_text = "The feline and canine demonstrate amicable relationships through collaborative recreational activities."
        
        common_metrics = self.analyzer.analyze(common_text)
        complex_metrics = self.analyzer.analyze(complex_text)
        
        # Common text should have lower Dale-Chall score (easier)
        self.assertLess(common_metrics.dale_chall, complex_metrics.dale_chall)
    
    def test_gunning_fog_calculation(self):
        """Test Gunning Fog Index calculation."""
        metrics = self.analyzer.analyze(self.mixed_text)
        
        # Should be reasonable for technical documentation
        self.assertGreater(metrics.gunning_fog, 5)
        self.assertLess(metrics.gunning_fog, 25)
    
    def test_smog_calculation(self):
        """Test SMOG Index calculation."""
        metrics = self.analyzer.analyze(self.mixed_text)
        
        # Should be in reasonable range
        self.assertGreater(metrics.smog_index, 0)
        self.assertLess(metrics.smog_index, 30)
    
    def test_ari_calculation(self):
        """Test Automated Readability Index calculation."""
        metrics = self.analyzer.analyze(self.mixed_text)
        
        # Should be in reasonable range
        self.assertGreater(metrics.automated_readability_index, 0)
        self.assertLess(metrics.automated_readability_index, 30)
    
    def test_markdown_cleaning(self):
        """Test markdown formatting removal for analysis."""
        markdown_text = """
        # Title
        
        This is **bold** and *italic* text.
        Here's a [link](http://example.com).
        
        ```python
        print("This is code")
        ```
        
        - List item 1
        - List item 2
        
        > This is a blockquote
        """
        
        cleaned = self.analyzer._clean_text_for_analysis(markdown_text)
        
        # Should remove markdown formatting
        self.assertNotIn('**', cleaned)
        self.assertNotIn('#', cleaned)
        self.assertNotIn('```', cleaned)
        self.assertNotIn('[', cleaned)
        self.assertNotIn('>', cleaned)
        self.assertIn('bold', cleaned)
        self.assertIn('italic', cleaned)
    
    def test_consensus_determination(self):
        """Test readability consensus determination."""
        # Test different grade levels
        metrics = ReadabilityMetrics()
        
        # Easy text
        metrics.average_grade_level = 6.0
        consensus = self.analyzer._determine_consensus(metrics)
        self.assertIn(consensus, ['very easy', 'easy'])
        
        # Difficult text
        metrics.average_grade_level = 18.0
        consensus = self.analyzer._determine_consensus(metrics)
        self.assertIn(consensus, ['difficult', 'very difficult'])
    
    def test_text_statistics_accuracy(self):
        """Test accuracy of basic text statistics."""
        test_text = "Hello world. This is a test sentence with multiple words."
        metrics = self.analyzer.analyze(test_text)
        
        # Verify basic counts are reasonable
        self.assertEqual(metrics.sentence_count, 2)
        self.assertGreater(metrics.word_count, 10)
        self.assertGreater(metrics.character_count, 50)
        self.assertGreater(metrics.syllable_count, 10)


class TestReadabilityEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for readability analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ReadabilityAnalyzer()
    
    def test_unicode_text_handling(self):
        """Test handling of Unicode characters."""
        unicode_text = "Hello 世界! This has émojis 😀 and accénted characters."
        
        # Should handle without errors
        metrics = self.analyzer.analyze(unicode_text)
        self.assertGreater(metrics.word_count, 0)
    
    def test_very_long_sentences(self):
        """Test handling of extremely long sentences."""
        long_sentence = "This is a very long sentence that goes on and on " * 20 + "."
        
        metrics = self.analyzer.analyze(long_sentence)
        self.assertEqual(metrics.sentence_count, 1)
        self.assertGreater(metrics.word_count, 100)
    
    def test_no_sentences(self):
        """Test text with no proper sentences."""
        no_sentences = "word1 word2 word3 word4"
        
        metrics = self.analyzer.analyze(no_sentences)
        # Should still process as one sentence
        self.assertGreaterEqual(metrics.sentence_count, 1)
        self.assertEqual(metrics.word_count, 4)
    
    def test_only_punctuation(self):
        """Test text with only punctuation."""
        punctuation_text = "!@#$%^&*().,;:"
        
        metrics = self.analyzer.analyze(punctuation_text)
        self.assertEqual(metrics.word_count, 0)
    
    def test_mixed_languages(self):
        """Test handling of mixed language content."""
        mixed_text = "Hello world. Bonjour le monde. 世界你好."
        
        # Should handle gracefully
        metrics = self.analyzer.analyze(mixed_text)
        self.assertGreater(metrics.word_count, 0)
        self.assertEqual(metrics.sentence_count, 3)


if __name__ == '__main__':
    unittest.main()