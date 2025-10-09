"""
Complexity and Sophistication Analysis for README Files

Quantifies README sophistication through rich formatting elements, document
structure complexity, and markdown feature utilization similar to readme-score.
"""

import re
from typing import List, Dict, Tuple, Set
from bs4 import BeautifulSoup
import markdown
from collections import Counter

from ..core.models import ComplexityMetrics


class ComplexityAnalyzer:
    """
    Advanced complexity analysis for README sophistication assessment.
    
    Implements scoring algorithms similar to readme-score (clayallsopp/readme-score)
    with comprehensive markdown element detection and formatting richness evaluation.
    """
    
    def __init__(self):
        """Initialize with element patterns and scoring weights."""
        self._define_element_patterns()
        self._define_scoring_weights()
    
    def _define_element_patterns(self) -> None:
        """Define regex patterns for detecting markdown elements."""
        self.element_patterns = {
            # Code elements
            'code_blocks': [
                r'```[\s\S]*?```',  # Fenced code blocks
                r'~~~[\s\S]*?~~~',  # Alternative fenced blocks
            ],
            'inline_code': [
                r'`[^`\n]+`',  # Inline code spans
            ],
            
            # Links and references
            'links': [
                r'\[([^\]]+)\]\([^\)]+\)',  # Inline links
                r'\[([^\]]+)\]\[[^\]]*\]',  # Reference links
            ],
            'reference_definitions': [
                r'^\s*\[[^\]]+\]:\s*\S+',  # Link reference definitions
            ],
            
            # Images
            'images': [
                r'!\[([^\]]*)\]\([^\)]+\)',  # Inline images
                r'!\[([^\]]*)\]\[[^\]]*\]',  # Reference images
            ],
            
            # Tables
            'tables': [
                r'\|.*\|.*\n\s*\|[-:\s|]+\|',  # Markdown tables with header separator
            ],
            
            # Lists
            'unordered_lists': [
                r'^\s*[-*+]\s+.+$',  # Unordered list items
            ],
            'ordered_lists': [
                r'^\s*\d+\.\s+.+$',  # Ordered list items
            ],
            'definition_lists': [
                r'^\S.*\n:\s+.+$',  # Definition lists (if supported)
            ],
            
            # Emphasis and formatting
            'bold_text': [
                r'\*\*([^*]+)\*\*',  # **bold**
                r'__([^_]+)__',      # __bold__
            ],
            'italic_text': [
                r'\*([^*\s][^*]*[^*\s])\*',  # *italic*
                r'_([^_\s][^_]*[^_\s])_',    # _italic_
            ],
            'strikethrough': [
                r'~~([^~]+)~~',  # ~~strikethrough~~
            ],
            
            # Blockquotes
            'blockquotes': [
                r'^\s*>.*$',  # Blockquote lines
            ],
            
            # Headings
            'headings': [
                r'^#{1,6}\s+.+$',  # ATX headings
                r'^.+\n[-=]+\s*$',  # Setext headings
            ],
            
            # Horizontal rules
            'horizontal_rules': [
                r'^\s*[-*_]{3,}\s*$',  # Horizontal rules
            ],
            
            # HTML elements
            'html_tags': [
                r'<[^>]+>',  # Any HTML tag
            ],
            'html_comments': [
                r'<!--[\s\S]*?-->',  # HTML comments
            ],
            
            # Advanced elements
            'footnotes': [
                r'\[\^[^\]]+\]',  # Footnote references
            ],
            'math_formulas': [
                r'\$\$[\s\S]*?\$\$',  # Display math
                r'\$[^$\n]+\$',       # Inline math
            ],
            'emojis': [
                r':[\w+_-]+:',  # Emoji shortcodes
                r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]',  # Unicode emojis
            ],
            
            # Task lists
            'task_lists': [
                r'^\s*[-*+]\s+\[[x\s]\]\s+.+$',  # Task list items
            ],
            
            # Badges and shields
            'badges': [
                r'!\[([^\]]*)\]\(https://img\.shields\.io[^\)]+\)',  # Shields.io badges
                r'!\[([^\]]*)\]\([^)]*badge[^)]*\)',  # Generic badges
            ],
        }
    
    def _define_scoring_weights(self) -> None:
        """Define scoring weights for different elements (similar to readme-score)."""
        self.element_weights = {
            'code_blocks': 5,      # High value for code examples
            'inline_code': 1,      # Moderate value for inline code
            'links': 2,            # Good for references and resources
            'images': 3,           # Visual elements add value
            'tables': 4,           # Structured data presentation
            'unordered_lists': 1,  # Basic organization
            'ordered_lists': 1,    # Basic organization
            'bold_text': 0.5,      # Basic formatting
            'italic_text': 0.5,    # Basic formatting
            'strikethrough': 1,    # Less common formatting
            'blockquotes': 2,      # Highlighted content
            'headings': 2,         # Document structure
            'horizontal_rules': 1, # Visual separation
            'html_tags': 2,        # Advanced formatting
            'footnotes': 3,        # Advanced documentation
            'math_formulas': 4,    # Specialized content
            'emojis': 1,           # Visual appeal
            'task_lists': 2,       # Interactive elements
            'badges': 3,           # Project status indicators
        }
    
    def analyze(self, text: str) -> ComplexityMetrics:
        """
        Perform comprehensive complexity analysis of README content.
        
        Args:
            text: Raw README text (markdown)
            
        Returns:
            ComplexityMetrics: Complete complexity assessment
        """
        metrics = ComplexityMetrics()
        
        # Count all element types
        element_counts = self._count_elements(text)
        
        # Populate metrics with counts
        self._populate_element_counts(metrics, element_counts)
        
        # Calculate document-level metrics
        self._calculate_document_metrics(text, metrics)
        
        # Calculate complexity scores
        self._calculate_complexity_scores(metrics, element_counts)
        
        return metrics
    
    def _count_elements(self, text: str) -> Dict[str, int]:
        """Count all markdown elements in the text."""
        counts = {}
        
        for element_type, patterns in self.element_patterns.items():
            total_count = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
                total_count += len(matches)
            counts[element_type] = total_count
        
        # Special handling for combined list types
        counts['lists'] = (counts.get('unordered_lists', 0) + 
                          counts.get('ordered_lists', 0) + 
                          counts.get('definition_lists', 0) + 
                          counts.get('task_lists', 0))
        
        return counts
    
    def _populate_element_counts(self, metrics: ComplexityMetrics, counts: Dict[str, int]) -> None:
        """Populate metrics object with element counts."""
        # Direct mappings
        metrics.code_block_count = counts.get('code_blocks', 0)
        metrics.inline_code_count = counts.get('inline_code', 0)
        metrics.link_count = counts.get('links', 0) + counts.get('reference_definitions', 0)
        metrics.image_count = counts.get('images', 0)
        metrics.table_count = counts.get('tables', 0)
        metrics.list_count = counts.get('lists', 0)
        
        # Formatting elements
        metrics.bold_text_count = counts.get('bold_text', 0)
        metrics.italic_text_count = counts.get('italic_text', 0)
        metrics.strikethrough_count = counts.get('strikethrough', 0)
        metrics.blockquote_count = counts.get('blockquotes', 0)
        
        # Advanced elements
        metrics.html_element_count = counts.get('html_tags', 0) + counts.get('html_comments', 0)
        metrics.emoji_count = counts.get('emojis', 0)
        metrics.math_formula_count = counts.get('math_formulas', 0)
    
    def _calculate_document_metrics(self, text: str, metrics: ComplexityMetrics) -> None:
        """Calculate overall document-level complexity metrics."""
        lines = text.split('\n')
        metrics.total_lines = len(lines)
        
        # Calculate non-empty lines
        non_empty_lines = sum(1 for line in lines if line.strip())
        
        # Markdown complexity based on element diversity
        unique_elements = sum(1 for count in [
            metrics.code_block_count,
            metrics.inline_code_count, 
            metrics.link_count,
            metrics.image_count,
            metrics.table_count,
            metrics.list_count,
            metrics.bold_text_count,
            metrics.italic_text_count,
            metrics.blockquote_count,
            metrics.html_element_count,
        ] if count > 0)
        
        # Markdown complexity score (0-100)
        max_elements = 10  # Maximum different element types we check
        metrics.markdown_complexity = (unique_elements / max_elements) * 100
        
        # Formatting diversity (richness of formatting)
        formatting_elements = [
            metrics.bold_text_count,
            metrics.italic_text_count,
            metrics.strikethrough_count,
            metrics.html_element_count,
            metrics.emoji_count,
        ]
        
        formatting_types = sum(1 for count in formatting_elements if count > 0)
        total_formatting = sum(formatting_elements)
        
        if total_formatting > 0:
            # Balance between variety and usage
            variety_score = (formatting_types / len(formatting_elements)) * 50
            usage_score = min(50, total_formatting * 2)  # Cap at 50 points
            metrics.formatting_diversity = variety_score + usage_score
        else:
            metrics.formatting_diversity = 0
    
    def _calculate_complexity_scores(self, metrics: ComplexityMetrics, counts: Dict[str, int]) -> None:
        """Calculate overall complexity and sophistication scores."""
        # Calculate weighted complexity score (similar to readme-score algorithm)
        total_weighted_score = 0
        total_possible_weight = 0
        
        for element_type, count in counts.items():
            if element_type in self.element_weights:
                weight = self.element_weights[element_type]
                total_weighted_score += count * weight
                total_possible_weight += weight * 5  # Assume max 5 of each element type
        
        # Normalize to 0-100 scale
        if total_possible_weight > 0:
            raw_score = (total_weighted_score / total_possible_weight) * 100
        else:
            raw_score = 0
        
        # Apply document length multiplier (longer docs can have higher complexity)
        length_multiplier = min(2.0, 1.0 + (metrics.total_lines / 500))
        
        # Final complexity score with diminishing returns
        metrics.complexity_score = min(100, raw_score * length_multiplier)
        
        # Determine sophistication level
        metrics.sophistication_level = self._determine_sophistication_level(
            metrics.complexity_score, 
            counts
        )
    
    def _determine_sophistication_level(self, score: float, counts: Dict[str, int]) -> str:
        """Determine sophistication level based on score and element presence."""
        # Check for advanced elements
        has_advanced_elements = any([
            counts.get('math_formulas', 0) > 0,
            counts.get('html_tags', 0) > 5,
            counts.get('footnotes', 0) > 0,
            counts.get('tables', 0) >= 2,
            counts.get('code_blocks', 0) >= 3,
        ])
        
        # Check for comprehensive documentation
        has_comprehensive_docs = any([
            counts.get('badges', 0) > 0,
            counts.get('images', 0) >= 2,
            counts.get('links', 0) >= 5,
            counts.get('headings', 0) >= 5,
        ])
        
        # Determine level
        if score >= 80 and has_advanced_elements:
            return "expert"
        elif score >= 60 and (has_advanced_elements or has_comprehensive_docs):
            return "advanced"
        elif score >= 40 or has_comprehensive_docs:
            return "intermediate"
        elif score >= 20:
            return "basic"
        else:
            return "minimal"
    
    def get_element_breakdown(self, text: str) -> Dict[str, Dict[str, int]]:
        """
        Get detailed breakdown of all elements for debugging/analysis.
        
        Returns:
            Dictionary with element categories and their counts
        """
        counts = self._count_elements(text)
        
        breakdown = {
            'content_elements': {
                'code_blocks': counts.get('code_blocks', 0),
                'inline_code': counts.get('inline_code', 0),
                'links': counts.get('links', 0),
                'images': counts.get('images', 0),
                'tables': counts.get('tables', 0),
                'lists': counts.get('lists', 0),
            },
            'formatting_elements': {
                'bold_text': counts.get('bold_text', 0),
                'italic_text': counts.get('italic_text', 0),
                'strikethrough': counts.get('strikethrough', 0),
                'blockquotes': counts.get('blockquotes', 0),
            },
            'structural_elements': {
                'headings': counts.get('headings', 0),
                'horizontal_rules': counts.get('horizontal_rules', 0),
            },
            'advanced_elements': {
                'html_tags': counts.get('html_tags', 0),
                'math_formulas': counts.get('math_formulas', 0),
                'footnotes': counts.get('footnotes', 0),
                'emojis': counts.get('emojis', 0),
                'badges': counts.get('badges', 0),
            }
        }
        
        return breakdown