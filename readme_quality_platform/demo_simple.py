#!/usr/bin/env python3
"""
Simple README Quality Platform Demo

A simplified demo that works with the current package structure.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demo_readability_analysis():
    """Demo the readability analysis component."""
    
    print("🚀 README Quality Platform - Readability Demo")
    print("=" * 50)
    
    try:
        from metrics.readability import ReadabilityAnalyzer
        
        # Sample content
        sample_text = """
        # Awesome Project
        
        This project provides a simple and easy-to-use solution for data processing.
        It includes powerful features that help developers work more efficiently.
        
        ## Installation
        
        You can install this project using pip:
        
        ```bash
        pip install awesome-project
        ```
        
        ## Usage
        
        Here's how to use the main functionality:
        
        ```python
        from awesome_project import DataProcessor
        
        processor = DataProcessor()
        result = processor.analyze(your_data)
        print(result)
        ```
        
        The system is designed to be user-friendly and accessible to developers
        of all skill levels. It provides comprehensive documentation and examples.
        """
        
        # Initialize analyzer
        analyzer = ReadabilityAnalyzer()
        
        # Perform analysis
        print("📊 Analyzing sample README content...")
        metrics = analyzer.analyze(sample_text)
        
        # Display results
        print("\n📈 Readability Analysis Results:")
        print(f"📖 Word Count: {metrics.word_count}")
        print(f"📝 Sentence Count: {metrics.sentence_count}")
        print(f"🎯 Flesch Reading Ease: {metrics.flesch_reading_ease:.1f}")
        print(f"🎓 Grade Level (Flesch-Kincaid): {metrics.flesch_kincaid_grade:.1f}")
        print(f"🌫️  Gunning Fog Index: {metrics.gunning_fog:.1f}")
        print(f"💨 SMOG Index: {metrics.smog_index:.1f}")
        print(f"📊 Dale-Chall Score: {metrics.dale_chall:.1f}")
        print(f"🤖 Automated Readability Index: {metrics.automated_readability_index:.1f}")
        print(f"🧠 Average Grade Level: {metrics.average_grade_level:.1f}")
        print(f"📋 Readability Consensus: {metrics.readability_consensus}")
        
        # Interpretation
        print("\n💡 Interpretation:")
        if metrics.flesch_reading_ease > 70:
            print("✅ Text is easy to read - accessible to most audiences")
        elif metrics.flesch_reading_ease > 60:
            print("⚠️  Text is fairly easy to read - good for general audiences")
        elif metrics.flesch_reading_ease > 50:
            print("🔶 Text has moderate difficulty - may need simplification")
        else:
            print("❌ Text is difficult to read - consider simplifying")
            
        return True
        
    except ImportError as e:
        print(f"❌ Could not import readability analyzer: {e}")
        return False


def demo_structural_analysis():
    """Demo the structural analysis component."""
    
    print("\n\n🏗️  Structural Analysis Demo")
    print("=" * 35)
    
    try:
        from metrics.structural import StructuralAnalyzer
        
        sample_readme = """
        # Project Title
        
        A comprehensive description of what this project does and why it's useful.
        
        ## Installation
        
        Installation instructions here.
        
        ## Usage
        
        Basic usage examples.
        
        ## Examples
        
        More detailed examples showing different use cases.
        
        ## API Reference
        
        Complete API documentation.
        
        ## Contributing
        
        Guidelines for contributors.
        
        ## License
        
        MIT License information.
        """
        
        analyzer = StructuralAnalyzer()
        metrics = analyzer.analyze(sample_readme)
        
        print("📊 Structural Analysis Results:")
        print(f"📋 Section Count: {metrics.section_count}")
        print(f"📏 Max Heading Depth: {metrics.max_heading_depth}")
        print(f"🎯 Completeness Score: {metrics.completeness_score:.1f}%")
        print(f"🏗️  Organization Score: {metrics.organization_score:.1f}%")
        print(f"⚖️  Heading Consistency: {metrics.heading_consistency:.1f}%")
        
        print("\n📦 Section Presence:")
        sections = [
            ("Title", metrics.has_title),
            ("Description", metrics.has_description), 
            ("Installation", metrics.has_installation),
            ("Usage", metrics.has_usage),
            ("Examples", metrics.has_examples),
            ("API Docs", metrics.has_api_docs),
            ("Contributing", metrics.has_contributing),
            ("License", metrics.has_license),
        ]
        
        for section, present in sections:
            status = "✅" if present else "❌"
            print(f"  {status} {section}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Could not import structural analyzer: {e}")
        return False


def demo_complexity_analysis():
    """Demo the complexity analysis component."""
    
    print("\n\n🔧 Complexity Analysis Demo")
    print("=" * 35)
    
    try:
        from metrics.complexity import ComplexityAnalyzer
        
        sample_readme = """
        # Advanced Project
        
        A **sophisticated** platform with *rich* formatting and ~~deprecated~~ features.
        
        ## Features
        
        - Feature one
        - Feature two  
        - Feature three
        
        ### Code Examples
        
        ```python
        def example_function():
            return "Hello World"
        ```
        
        ```bash
        pip install example-package
        ```
        
        ## Links and Resources
        
        - [Documentation](https://docs.example.com)
        - [GitHub](https://github.com/user/repo)
        - [Issues](https://github.com/user/repo/issues)
        
        ## Data Table
        
        | Feature | Status | Notes |
        |---------|--------|-------|
        | API     | ✅     | Ready |
        | CLI     | 🔄     | Beta  |
        | Web     | ❌     | TODO  |
        
        > **Note**: This is an important blockquote with critical information.
        
        ![Architecture Diagram](https://example.com/diagram.png)
        
        ## Mathematical Formulas
        
        The complexity is calculated as: $O(n^2)$
        
        $$E = mc^2$$
        """
        
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze(sample_readme)
        
        print("📊 Complexity Analysis Results:")
        print(f"📝 Total Lines: {metrics.total_lines}")
        print(f"🔢 Code Blocks: {metrics.code_block_count}")
        print(f"💻 Inline Code: {metrics.inline_code_count}")
        print(f"🔗 Links: {metrics.link_count}")
        print(f"🖼️  Images: {metrics.image_count}")
        print(f"📊 Tables: {metrics.table_count}")
        print(f"📋 Lists: {metrics.list_count}")
        print(f"💪 Bold Text: {metrics.bold_text_count}")
        print(f"📚 Blockquotes: {metrics.blockquote_count}")
        print(f"🧮 Math Formulas: {metrics.math_formula_count}")
        print(f"🎨 Markdown Complexity: {metrics.markdown_complexity:.1f}%")
        print(f"🌟 Overall Complexity: {metrics.complexity_score:.1f}/100")
        print(f"🎓 Sophistication Level: {metrics.sophistication_level}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import complexity analyzer: {e}")
        return False


def demo_configuration():
    """Demo the configuration system."""
    
    print("\n\n⚙️  Configuration Demo")
    print("=" * 25)
    
    try:
        from core.config import Config
        
        # Create default config
        config = Config()
        
        print("📋 Default Configuration:")
        print(f"🎯 Scoring Weights:")
        for dimension, weight in config.analysis.scoring_weights.items():
            print(f"  {dimension}: {weight:.2f}")
        
        print(f"\n🎚️  Quality Thresholds:")
        for level, threshold in config.analysis.quality_thresholds.items():
            print(f"  {level}: {threshold}")
        
        # Demonstrate custom weights
        print("\n🎛️  Custom Weights Example:")
        custom_weights = config.create_custom_weights(
            readability=0.30,
            structural=0.40,
            complexity=0.15,
            consistency=0.15
        )
        print("Custom configuration (emphasizing readability and structure):")
        for dimension, weight in custom_weights.items():
            print(f"  {dimension}: {weight:.2f}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Could not import configuration: {e}")
        return False


def main():
    """Run all demos."""
    
    print("🎯 README Quality Platform - Component Demos\n")
    
    success_count = 0
    total_demos = 0
    
    # Run individual component demos
    demos = [
        ("Readability Analysis", demo_readability_analysis),
        ("Structural Analysis", demo_structural_analysis), 
        ("Complexity Analysis", demo_complexity_analysis),
        ("Configuration System", demo_configuration),
    ]
    
    for name, demo_func in demos:
        total_demos += 1
        try:
            if demo_func():
                success_count += 1
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    # Summary
    print(f"\n\n📊 Demo Summary")
    print("=" * 20)
    print(f"✅ Successful: {success_count}/{total_demos}")
    print(f"❌ Failed: {total_demos - success_count}/{total_demos}")
    
    if success_count == total_demos:
        print("\n🎉 All demos completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Install full dependencies: pip install -r requirements.txt")
        print("  2. Try the complete platform integration")
        print("  3. Set up the web API and dashboard")
        print("  4. Configure GitHub Actions for your repositories")
    else:
        print("\n⚠️  Some demos failed - check dependencies and imports")
        print("💡 Try installing missing packages:")
        print("   pip install textstat beautifulsoup4 markdown nltk")


if __name__ == "__main__":
    main()