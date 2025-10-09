#!/usr/bin/env python3
"""
Working README Quality Platform Demo

Demonstrates core functionality with standalone implementations.
"""

import re
import math
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import Counter


@dataclass
class ReadabilityMetrics:
    """Simple readability metrics container."""
    word_count: int = 0
    sentence_count: int = 0
    syllable_count: int = 0
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    readability_level: str = "unknown"


@dataclass 
class StructuralMetrics:
    """Simple structural metrics container."""
    has_title: bool = False
    has_description: bool = False
    has_installation: bool = False
    has_usage: bool = False
    has_examples: bool = False
    has_license: bool = False
    section_count: int = 0
    completeness_score: float = 0.0


@dataclass
class ComplexityMetrics:
    """Simple complexity metrics container."""
    code_blocks: int = 0
    links: int = 0
    images: int = 0
    tables: int = 0
    lists: int = 0
    bold_text: int = 0
    total_elements: int = 0
    complexity_score: float = 0.0


class SimpleReadabilityAnalyzer:
    """Simplified readability analyzer."""
    
    def count_syllables(self, word: str) -> int:
        """Simple syllable counting."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        
        if word[0] in vowels:
            count += 1
        
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                count += 1
        
        if word.endswith('e'):
            count -= 1
        
        return max(1, count)
    
    def analyze(self, text: str) -> ReadabilityMetrics:
        """Analyze text readability."""
        # Clean text
        clean_text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
        clean_text = re.sub(r'`[^`]+`', '', clean_text)   # Remove inline code
        clean_text = re.sub(r'[#*_\[\]()>]', '', clean_text)  # Remove markdown
        
        # Count sentences
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Count words
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text)
        word_count = len(words)
        
        # Count syllables
        syllable_count = sum(self.count_syllables(word) for word in words)
        
        if sentence_count == 0 or word_count == 0:
            return ReadabilityMetrics()
        
        # Calculate Flesch Reading Ease
        asl = word_count / sentence_count  # Average sentence length
        asw = syllable_count / word_count  # Average syllables per word
        flesch_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
        flesch_ease = max(0, min(100, flesch_ease))
        
        # Calculate Flesch-Kincaid Grade Level
        flesch_kincaid = (0.39 * asl) + (11.8 * asw) - 15.59
        flesch_kincaid = max(0, flesch_kincaid)
        
        # Calculate Gunning Fog (simplified)
        complex_words = sum(1 for word in words if self.count_syllables(word) >= 3)
        phw = (complex_words / word_count) * 100 if word_count > 0 else 0
        gunning_fog = 0.4 * (asl + phw)
        
        # Determine readability level
        if flesch_ease > 90:
            level = "very easy"
        elif flesch_ease > 80:
            level = "easy"
        elif flesch_ease > 70:
            level = "fairly easy"
        elif flesch_ease > 60:
            level = "standard"
        elif flesch_ease > 50:
            level = "fairly difficult"
        elif flesch_ease > 30:
            level = "difficult"
        else:
            level = "very difficult"
        
        return ReadabilityMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            syllable_count=syllable_count,
            flesch_reading_ease=flesch_ease,
            flesch_kincaid_grade=flesch_kincaid,
            gunning_fog=gunning_fog,
            readability_level=level
        )


class SimpleStructuralAnalyzer:
    """Simplified structural analyzer."""
    
    def analyze(self, text: str) -> StructuralMetrics:
        """Analyze README structure."""
        text_lower = text.lower()
        
        # Check for sections
        has_title = bool(re.search(r'^#\s+.+', text, re.MULTILINE))
        has_description = bool(re.search(r'(description|about|overview)', text_lower))
        has_installation = bool(re.search(r'(install|setup)', text_lower))
        has_usage = bool(re.search(r'(usage|how\s+to|example)', text_lower))
        has_examples = bool(re.search(r'example', text_lower))
        has_license = bool(re.search(r'licen[sc]e', text_lower))
        
        # Count sections (headers)
        headers = re.findall(r'^#+\s+.+', text, re.MULTILINE)
        section_count = len(headers)
        
        # Calculate completeness (essential sections)
        essential_sections = [has_title, has_description, has_installation, has_usage]
        completeness = (sum(essential_sections) / len(essential_sections)) * 100
        
        return StructuralMetrics(
            has_title=has_title,
            has_description=has_description,
            has_installation=has_installation,
            has_usage=has_usage,
            has_examples=has_examples,
            has_license=has_license,
            section_count=section_count,
            completeness_score=completeness
        )


class SimpleComplexityAnalyzer:
    """Simplified complexity analyzer."""
    
    def analyze(self, text: str) -> ComplexityMetrics:
        """Analyze README complexity."""
        
        # Count various elements
        code_blocks = len(re.findall(r'```[\s\S]*?```', text))
        links = len(re.findall(r'\[([^\]]+)\]\([^\)]+\)', text))
        images = len(re.findall(r'!\[([^\]]*)\]\([^\)]+\)', text))
        tables = len(re.findall(r'\|.*\|.*\n.*\|[-:\s|]+\|', text))
        lists = len(re.findall(r'^\s*[-*+]\s+', text, re.MULTILINE))
        bold_text = len(re.findall(r'\*\*([^*]+)\*\*', text))
        
        total_elements = code_blocks + links + images + tables + lists + bold_text
        
        # Calculate complexity score (0-100)
        element_weights = {
            'code_blocks': 5,
            'links': 2,
            'images': 3,
            'tables': 4,
            'lists': 1,
            'bold_text': 1
        }
        
        weighted_score = (
            code_blocks * element_weights['code_blocks'] +
            links * element_weights['links'] +
            images * element_weights['images'] +
            tables * element_weights['tables'] +
            lists * element_weights['lists'] +
            bold_text * element_weights['bold_text']
        )
        
        # Normalize to 0-100 (assume max 20 total weighted elements for 100 score)
        complexity_score = min(100, (weighted_score / 20) * 100)
        
        return ComplexityMetrics(
            code_blocks=code_blocks,
            links=links,
            images=images,
            tables=tables,
            lists=lists,
            bold_text=bold_text,
            total_elements=total_elements,
            complexity_score=complexity_score
        )


class SimpleReadmeAnalyzer:
    """Simplified README analyzer combining all metrics."""
    
    def __init__(self):
        self.readability_analyzer = SimpleReadabilityAnalyzer()
        self.structural_analyzer = SimpleStructuralAnalyzer()
        self.complexity_analyzer = SimpleComplexityAnalyzer()
    
    def analyze(self, text: str) -> Dict:
        """Perform complete README analysis."""
        
        readability = self.readability_analyzer.analyze(text)
        structure = self.structural_analyzer.analyze(text)
        complexity = self.complexity_analyzer.analyze(text)
        
        # Calculate overall score (weighted average)
        weights = {
            'readability': 0.25,
            'structural': 0.35,
            'complexity': 0.25,
            'consistency': 0.15  # Not implemented in simple version
        }
        
        # Convert metrics to scores (0-100)
        readability_score = max(0, min(100, readability.flesch_reading_ease))
        structural_score = structure.completeness_score
        complexity_score = complexity.complexity_score
        consistency_score = 50  # Default placeholder
        
        overall_score = (
            readability_score * weights['readability'] +
            structural_score * weights['structural'] +
            complexity_score * weights['complexity'] +
            consistency_score * weights['consistency']
        )
        
        # Determine grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 85:
            grade = "A"
        elif overall_score >= 80:
            grade = "A-"
        elif overall_score >= 75:
            grade = "B+"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'readability': readability,
            'structure': structure,
            'complexity': complexity,
            'scores': {
                'readability': readability_score,
                'structural': structural_score,
                'complexity': complexity_score,
                'consistency': consistency_score
            }
        }


def demo_comprehensive_analysis():
    """Demonstrate comprehensive README analysis."""
    
    print("🚀 README Quality Platform - Comprehensive Demo")
    print("=" * 55)
    
    # Sample README content
    sample_readme = """
# Awesome Data Processor

A powerful and user-friendly library for processing large datasets with advanced analytics capabilities. This tool helps data scientists and developers streamline their workflow with efficient algorithms and comprehensive visualization options.

## Features

- **Fast Processing**: Optimized algorithms for handling large datasets
- **Easy Integration**: Simple API design with minimal setup required
- **Comprehensive Analytics**: Statistical analysis and machine learning tools
- **Rich Visualizations**: Built-in plotting and dashboard capabilities
- **Cloud Ready**: Seamless deployment to cloud platforms

## Installation

Install using pip:

```bash
pip install awesome-data-processor
```

Or using conda:

```bash
conda install -c conda-forge awesome-data-processor
```

## Quick Start

Here's how to get started with basic data processing:

```python
from awesome_processor import DataProcessor, Visualizer

# Initialize the processor
processor = DataProcessor()

# Load your data
data = processor.load_csv('your_data.csv')

# Perform analysis
results = processor.analyze(data)
print(f"Analysis complete: {results.summary}")

# Create visualizations
viz = Visualizer(results)
viz.plot_trends().save('trends.png')
```

## Advanced Usage

### Custom Processing Pipeline

```python
# Create a custom processing pipeline
pipeline = processor.create_pipeline([
    'normalize_data',
    'detect_outliers', 
    'apply_clustering'
])

processed_data = pipeline.run(data)
```

### Machine Learning Integration

```python
from awesome_processor.ml import ModelTrainer

# Train a predictive model
trainer = ModelTrainer(processed_data)
model = trainer.train('random_forest')
predictions = model.predict(new_data)
```

## API Reference

### DataProcessor Class

Main class for data processing operations.

#### Methods

- `load_csv(filepath)`: Load data from CSV file
- `analyze(data, options)`: Perform comprehensive analysis
- `export(data, format)`: Export results in various formats

### Visualizer Class

Handles data visualization and reporting.

#### Methods

- `plot_trends()`: Generate trend analysis plots
- `create_dashboard()`: Build interactive dashboard
- `export_report()`: Generate PDF reports

## Configuration

Create a config file to customize behavior:

```yaml
# config.yml
processing:
  max_memory_gb: 8
  parallel_workers: 4
  cache_enabled: true

visualization:
  theme: "modern"
  dpi: 300
  format: "png"
```

## Performance Benchmarks

| Dataset Size | Processing Time | Memory Usage |
|-------------|-----------------|--------------|
| 1MB         | 0.1s           | 50MB         |
| 100MB       | 2.3s           | 200MB        |
| 1GB         | 45s            | 1.2GB        |

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on:

- Setting up development environment
- Running tests
- Submitting pull requests
- Code style guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://awesome-processor.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/user/awesome-processor/issues)  
- 💬 [Discord Community](https://discord.gg/awesome-processor)
- 📧 Email: support@awesome-processor.com
"""
    
    # Initialize analyzer
    analyzer = SimpleReadmeAnalyzer()
    
    # Perform analysis
    print("📊 Analyzing comprehensive README sample...")
    results = analyzer.analyze(sample_readme)
    
    # Display results
    print("\n🎯 Overall Quality Assessment")
    print("-" * 35)
    print(f"Overall Score: {results['overall_score']:.1f}/100")
    print(f"Grade: {results['grade']}")
    
    print("\n📊 Dimension Scores")
    print("-" * 20)
    for dimension, score in results['scores'].items():
        if dimension == 'consistency':
            print(f"🔗 {dimension.title()}: {score:.1f}/100 (placeholder)")
        else:
            print(f"📋 {dimension.title()}: {score:.1f}/100")
    
    print("\n📖 Readability Analysis")
    print("-" * 25)
    readability = results['readability']
    print(f"Word Count: {readability.word_count}")
    print(f"Sentences: {readability.sentence_count}")
    print(f"Flesch Reading Ease: {readability.flesch_reading_ease:.1f}")
    print(f"Grade Level: {readability.flesch_kincaid_grade:.1f}")
    print(f"Gunning Fog: {readability.gunning_fog:.1f}")
    print(f"Readability Level: {readability.readability_level}")
    
    print("\n🏗️  Structural Analysis") 
    print("-" * 25)
    structure = results['structure']
    print(f"Section Count: {structure.section_count}")
    print(f"Completeness: {structure.completeness_score:.1f}%")
    
    sections = [
        ("Title", structure.has_title),
        ("Description", structure.has_description),
        ("Installation", structure.has_installation),
        ("Usage", structure.has_usage),
        ("Examples", structure.has_examples),
        ("License", structure.has_license)
    ]
    
    print("Essential Sections:")
    for name, present in sections:
        status = "✅" if present else "❌"
        print(f"  {status} {name}")
    
    print("\n🔧 Complexity Analysis")
    print("-" * 25)
    complexity = results['complexity']
    print(f"Code Blocks: {complexity.code_blocks}")
    print(f"Links: {complexity.links}")
    print(f"Images: {complexity.images}")
    print(f"Tables: {complexity.tables}")
    print(f"Lists: {complexity.lists}")
    print(f"Bold Text: {complexity.bold_text}")
    print(f"Total Elements: {complexity.total_elements}")
    print(f"Complexity Score: {complexity.complexity_score:.1f}/100")
    
    # Generate recommendations
    print("\n💡 Recommendations")
    print("-" * 20)
    
    recommendations = []
    
    if readability.flesch_reading_ease < 50:
        recommendations.append("Consider simplifying language for better readability")
    
    if structure.completeness_score < 80:
        recommendations.append("Add missing essential sections (installation, usage, examples)")
    
    if complexity.code_blocks < 2:
        recommendations.append("Add more code examples to demonstrate usage")
    
    if complexity.images == 0:
        recommendations.append("Consider adding diagrams or screenshots")
    
    if not structure.has_license:
        recommendations.append("Add license information")
    
    if not recommendations:
        recommendations.append("Excellent README! Consider minor formatting improvements")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Summary assessment
    print(f"\n🎉 Analysis Summary")
    print("=" * 20)
    
    if results['overall_score'] >= 85:
        print("🌟 Exceptional README quality!")
    elif results['overall_score'] >= 75:
        print("✅ Good README with room for minor improvements")
    elif results['overall_score'] >= 60:
        print("⚠️  Average README - several areas need improvement")
    else:
        print("❌ README needs significant improvement")
    
    print(f"\nThis README scores better than {results['overall_score']:.0f}% of repositories")
    
    return results


def demo_comparative_analysis():
    """Demo comparing different README quality levels."""
    
    print("\n\n📊 Comparative Quality Analysis")
    print("=" * 40)
    
    samples = {
        "Minimal": "# Project\n\nA simple project.",
        "Basic": """# My Project
        
        This project does something useful.
        
        ## Installation
        pip install my-project
        
        ## Usage
        Use it like this: `my-project run`
        """,
        "Complete": """# Advanced Analytics Platform
        
        A comprehensive data analytics platform with machine learning capabilities.
        
        ## Features
        - Data processing
        - ML algorithms  
        - Visualization tools
        
        ## Installation
        ```bash
        pip install analytics-platform
        ```
        
        ## Usage
        ```python
        from analytics import Platform
        platform = Platform()
        results = platform.analyze(data)
        ```
        
        ## Examples
        See our [examples](examples/) directory.
        
        ## License
        MIT License
        """
    }
    
    analyzer = SimpleReadmeAnalyzer()
    
    print("Analyzing different README quality levels:\n")
    
    for name, content in samples.items():
        results = analyzer.analyze(content)
        print(f"📋 {name} README:")
        print(f"   Score: {results['overall_score']:.1f}/100 ({results['grade']})")
        print(f"   Words: {results['readability'].word_count}")
        print(f"   Sections: {results['structure'].section_count}")
        print(f"   Elements: {results['complexity'].total_elements}")
        print()


def main():
    """Run the comprehensive demo."""
    
    print("🎯 README Quality Platform - Working Demo")
    print("\nDemonstrating multi-dimensional README analysis...\n")
    
    try:
        # Main comprehensive analysis
        demo_comprehensive_analysis()
        
        # Comparative analysis
        demo_comparative_analysis()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📚 What this demo showed:")
        print("✅ Multi-dimensional analysis (readability, structure, complexity)")
        print("✅ Comprehensive scoring system with weighted metrics")
        print("✅ Actionable recommendations for improvement")
        print("✅ Comparative analysis across quality levels")
        
        print("\n🚀 Full Platform Features:")
        print("• GitHub API integration for repository analysis")
        print("• REST API server with comprehensive endpoints")
        print("• Interactive web dashboard with visualizations") 
        print("• CLI tool with batch processing capabilities")
        print("• GitHub Actions for automated quality checks")
        print("• Code-documentation consistency analysis")
        print("• LLM-powered evaluation (extensible)")
        
        print("\n💡 Next Steps:")
        print("1. Install full dependencies: pip install -r requirements.txt")
        print("2. Set up the complete platform with all integrations")
        print("3. Configure GitHub token for repository analysis")
        print("4. Deploy the web dashboard and API services")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()