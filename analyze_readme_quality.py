#!/usr/bin/env python3
"""
Simple README Quality Analyzer
Analyzes our current README.md to identify improvement areas for 100/100 score
"""

import re
import os
import sys
from typing import Dict, List, Any

# Try to use textstat if available, otherwise implement basic metrics
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    print("Note: textstat not available, using basic metrics")

class SimpleREADMEAnalyzer:
    """Simple README analyzer focusing on key quality metrics"""
    
    def __init__(self):
        # Weights for different aspects (must sum to 1.0)
        self.weights = {
            'readability': 0.25,
            'structure': 0.30,
            'complexity': 0.20,
            'consistency': 0.25
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze README file and return comprehensive metrics"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.analyze_content(content)
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze README content and return metrics"""
        
        # Basic text metrics
        lines = content.split('\n')
        words = re.findall(r'\b\w+\b', content.lower())
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Content analysis
        readability_score = self._analyze_readability(content, words, sentences)
        structure_score = self._analyze_structure(content, lines)
        complexity_score = self._analyze_complexity(content)
        consistency_score = self._analyze_consistency(content)
        
        # Calculate overall score
        overall_score = (
            readability_score * self.weights['readability'] +
            structure_score * self.weights['structure'] +
            complexity_score * self.weights['complexity'] +
            consistency_score * self.weights['consistency']
        )
        
        return {
            'overall_score': overall_score,
            'grade': self._score_to_grade(overall_score),
            'metrics': {
                'readability': readability_score,
                'structure': structure_score,  
                'complexity': complexity_score,
                'consistency': consistency_score
            },
            'details': {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'line_count': len(lines),
                'character_count': len(content)
            },
            'recommendations': self._generate_recommendations(
                readability_score, structure_score, complexity_score, consistency_score
            )
        }
    
    def _analyze_readability(self, content: str, words: List[str], sentences: List[str]) -> float:
        """Analyze readability metrics"""
        if TEXTSTAT_AVAILABLE:
            # Use textstat for advanced metrics
            flesch_score = textstat.flesch_reading_ease(content)
            # Convert Flesch (0-100, higher=better) to 0-100 score
            readability = max(0, min(100, flesch_score))
        else:
            # Basic readability estimate
            if not words or not sentences:
                return 0.0
            
            avg_words_per_sentence = len(words) / len(sentences)
            long_words = len([w for w in words if len(w) > 6])
            long_word_ratio = long_words / len(words) if words else 0
            
            # Simple readability formula (higher avg words and long words = lower score)
            readability = max(0, 100 - (avg_words_per_sentence * 2) - (long_word_ratio * 100))
        
        return readability
    
    def _analyze_structure(self, content: str, lines: List[str]) -> float:
        """Analyze structural completeness and organization"""
        score = 0.0
        
        # Essential sections (30 points each)
        essential_sections = [
            r'#.*?overview|#.*?description',  # Project overview
            r'#.*?install',  # Installation
            r'#.*?usage|#.*?quick.*?start',  # Usage/Quick start
            r'#.*?example',  # Examples
            r'#.*?license',  # License
        ]
        
        for pattern in essential_sections:
            if re.search(pattern, content, re.IGNORECASE):
                score += 15  # 75 points total for essentials
        
        # Bonus sections (5 points each)  
        bonus_sections = [
            r'#.*?contribut',  # Contributing
            r'#.*?api|#.*?reference',  # API docs
            r'#.*?test',  # Testing
            r'#.*?changelog|#.*?release',  # Changelog
            r'!\[.*?\]',  # Badges (images)
        ]
        
        for pattern in bonus_sections:
            if re.search(pattern, content, re.IGNORECASE):
                score += 5  # 25 points total for bonus
        
        return min(100.0, score)
    
    def _analyze_complexity(self, content: str) -> float:
        """Analyze content complexity and richness"""
        score = 0.0
        
        # Code blocks (20 points)
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        score += min(20, code_blocks * 3)
        
        # Links (15 points)
        links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        score += min(15, links * 1)
        
        # Images (15 points)
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        score += min(15, images * 5)
        
        # Tables (15 points)
        tables = len(re.findall(r'\|.*?\|', content))
        score += min(15, tables * 2)
        
        # Lists (10 points)
        lists = len(re.findall(r'^\s*[-*+]\s|^\s*\d+\.\s', content, re.MULTILINE))
        score += min(10, lists * 0.5)
        
        # Formatting (15 points)
        bold_text = len(re.findall(r'\*\*.*?\*\*', content))
        italic_text = len(re.findall(r'\*.*?\*', content))
        score += min(15, (bold_text + italic_text) * 0.5)
        
        # Emojis (10 points)
        emojis = len(re.findall(r'[🎯🔬🧬⚡🚀📊🎉✅❌🔧🌟📈📋🔗💻🧪📚📄🙏📬🏆🎨🛠️🔌🌐💡🧠📁🎊🔰📖]', content))
        score += min(10, emojis * 0.5)
        
        return min(100.0, score)
    
    def _analyze_consistency(self, content: str) -> float:
        """Analyze code-documentation consistency"""
        # This is a simplified consistency check
        # Look for code elements mentioned in README
        
        score = 50.0  # Base score
        
        # Check for class/function mentions
        class_mentions = len(re.findall(r'`[A-Z][a-zA-Z]*`', content))  # PascalCase classes
        function_mentions = len(re.findall(r'`[a-z_][a-z0-9_]*\(\)`', content))  # snake_case functions
        
        # Bonus for code element documentation
        if class_mentions > 0:
            score += min(25, class_mentions * 2)
        if function_mentions > 0:
            score += min(25, function_mentions * 2)
        
        return min(100.0, score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 97: return "A+"
        elif score >= 93: return "A"
        elif score >= 90: return "A-"
        elif score >= 87: return "B+"
        elif score >= 83: return "B"
        elif score >= 80: return "B-"
        elif score >= 77: return "C+"
        elif score >= 73: return "C" 
        elif score >= 70: return "C-"
        elif score >= 60: return "D"
        else: return "F"
    
    def _generate_recommendations(self, readability: float, structure: float, 
                                complexity: float, consistency: float) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if readability < 80:
            recommendations.append(f"📖 Improve readability (current: {readability:.1f}/100): Use shorter sentences, simpler words, and more white space")
        
        if structure < 90:
            recommendations.append(f"🏗️ Enhance structure (current: {structure:.1f}/100): Add missing essential sections like API documentation, examples, or contributing guidelines")
        
        if complexity < 85:
            recommendations.append(f"🎨 Increase content richness (current: {complexity:.1f}/100): Add more code examples, diagrams, tables, or visual elements")
        
        if consistency < 85:
            recommendations.append(f"🔗 Improve consistency (current: {consistency:.1f}/100): Document more code elements, APIs, and implementation details")
        
        # High-impact recommendations for reaching 99-100
        if max(readability, structure, complexity, consistency) < 95:
            recommendations.extend([
                "🎯 For 99-100 score: Add comprehensive API documentation with all classes/methods",
                "🚀 For 99-100 score: Include visual diagrams showing system architecture", 
                "📊 For 99-100 score: Add performance benchmarks and comparison tables",
                "🧪 For 99-100 score: Include detailed testing and validation results",
                "🌟 For 99-100 score: Add comprehensive examples covering all use cases"
            ])
        
        return recommendations

def main():
    """Main analysis function"""
    if len(sys.argv) != 2:
        print("Usage: python analyze_readme_quality.py <README_FILE>")
        sys.exit(1)
    
    readme_file = sys.argv[1]
    if not os.path.exists(readme_file):
        print(f"Error: File '{readme_file}' not found")
        sys.exit(1)
    
    analyzer = SimpleREADMEAnalyzer()
    results = analyzer.analyze_file(readme_file)
    
    # Display results
    print("🎯 README QUALITY ANALYSIS RESULTS")
    print("=" * 50)
    print(f"📊 Overall Score: {results['overall_score']:.1f}/100")
    print(f"🎯 Grade: {results['grade']}")
    print()
    
    print("📈 Dimension Breakdown:")
    for dimension, score in results['metrics'].items():
        print(f"  📋 {dimension.title()}: {score:.1f}/100")
    print()
    
    print("📊 Content Statistics:")
    for stat, value in results['details'].items():
        print(f"  • {stat.replace('_', ' ').title()}: {value:,}")
    print()
    
    print("💡 Recommendations for Improvement:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()
    
    # Specific guidance for reaching 100/100
    current_score = results['overall_score']
    points_needed = 100 - current_score
    
    if current_score >= 95:
        print("🌟 EXCELLENT! You're very close to perfect!")
        print(f"   Need just {points_needed:.1f} more points for 100/100")
    elif current_score >= 90:
        print("🎉 GREAT WORK! Almost there!")
        print(f"   Need {points_needed:.1f} points for perfect score")
    else:
        print(f"📈 Progress needed: {points_needed:.1f} points to reach 100/100")
    
    print("\n🎯 Strategic Focus Areas:")
    
    # Identify weakest areas
    metrics = results['metrics']
    sorted_metrics = sorted(metrics.items(), key=lambda x: x[1])
    
    for dimension, score in sorted_metrics[:2]:  # Focus on 2 weakest areas
        weight = analyzer.weights[dimension]
        max_improvement = (100 - score) * weight
        print(f"  🔥 {dimension.title()}: {max_improvement:.1f} potential points (current: {score:.1f}/100)")

if __name__ == '__main__':
    main()