#!/usr/bin/env python3
"""
README Quality Platform Demo Script

Demonstrates the comprehensive capabilities of the README Quality Platform
with examples of all analysis dimensions and output formats.
"""

import sys
import json
from pathlib import Path

# Add the platform to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import ReadmeAnalyzer
from core.config import Config
from analyzers.github import GitHubAnalyzer


def demo_basic_analysis():
    """Demonstrate basic README analysis functionality."""
    
    print("🚀 README Quality Platform Demo")
    print("=" * 50)
    
    # Sample README content for testing
    sample_readme = """
# Awesome Project

A comprehensive solution for managing data workflows with advanced analytics capabilities.

## Installation

```bash
pip install awesome-project
```

## Usage

```python
from awesome_project import DataProcessor

processor = DataProcessor()
result = processor.analyze(data)
print(result.summary)
```

## Features

- **Fast Processing**: Optimized algorithms for large datasets
- **Easy Integration**: Simple API with comprehensive documentation
- **Scalable**: Designed for enterprise-scale deployments
- **Extensible**: Plugin architecture for custom functionality

## API Reference

### DataProcessor Class

The main class for data processing operations.

#### Methods

- `analyze(data)`: Performs comprehensive data analysis
- `export(format)`: Exports results in various formats
- `configure(options)`: Configures processing parameters

## Contributing

We welcome contributions! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.
"""
    
    # Initialize analyzer
    print("\n🔧 Initializing README Quality Analyzer...")
    analyzer = ReadmeAnalyzer()
    
    # Perform analysis
    print("📊 Analyzing sample README content...")
    analysis = analyzer.analyze_content(
        content=sample_readme,
        readme_path="sample_README.md"
    )
    
    # Display results
    print("\n📈 Analysis Results:")
    print(f"Overall Score: {analysis.quality.overall_score:.1f}/100 ({analysis.quality.grade_level})")
    
    print("\n📋 Dimension Scores:")
    print(f"  📖 Readability: {analysis.quality.readability_score:.1f}/100")
    print(f"  🏗️  Structure:   {analysis.quality.structural_score:.1f}/100")
    print(f"  🔧 Complexity:  {analysis.quality.complexity_score:.1f}/100")
    print(f"  🔗 Consistency: {analysis.quality.consistency_score:.1f}/100")
    
    print("\n📊 Key Metrics:")
    print(f"  Word Count: {analysis.readability.word_count}")
    print(f"  Readability Level: {analysis.readability.readability_consensus}")
    print(f"  Flesch Reading Ease: {analysis.readability.flesch_reading_ease:.1f}")
    print(f"  Grade Level: {analysis.readability.average_grade_level:.1f}")
    print(f"  Sections: {analysis.structure.section_count}")
    print(f"  Completeness: {analysis.structure.completeness_score:.1f}%")
    
    if analysis.quality.recommendations:
        print("\n💡 Top Recommendations:")
        for i, rec in enumerate(analysis.quality.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    if analysis.quality.strengths:
        print("\n✅ Strengths:")
        for strength in analysis.quality.strengths:
            print(f"  • {strength}")
    
    print(f"\n⏱️  Analysis completed in {analysis.analysis_duration_ms:.0f}ms")
    
    return analysis


def demo_custom_weights():
    """Demonstrate custom scoring weights configuration."""
    
    print("\n\n🎛️  Custom Weights Demo")
    print("=" * 30)
    
    # Create custom configuration emphasizing structure
    config = Config()
    config.analysis.scoring_weights = {
        'readability': 0.15,
        'structural': 0.50,  # Emphasize structure
        'complexity': 0.15,
        'consistency': 0.20,
    }
    
    analyzer = ReadmeAnalyzer(config.get_analyzer_config())
    
    sample_content = """
# Project Title

Brief description here.

## Installation
pip install project

## Usage
Basic usage example.
"""
    
    analysis = analyzer.analyze_content(sample_content)
    
    print("📊 Analysis with Structure-Focused Weights:")
    print(f"  Overall Score: {analysis.quality.overall_score:.1f}/100")
    print(f"  Weights Used: {analysis.quality.weights}")
    print(f"  Structure Score Impact: {analysis.quality.structural_score * 0.5:.1f} points")


def demo_github_integration():
    """Demonstrate GitHub repository analysis (requires token)."""
    
    print("\n\n🐙 GitHub Integration Demo")
    print("=" * 30)
    
    # This would require a GitHub token in real usage
    print("ℹ️  GitHub integration requires GITHUB_TOKEN environment variable")
    print("📝 Example usage:")
    print("""
    from analyzers.github import GitHubAnalyzer
    
    github_analyzer = GitHubAnalyzer("your_github_token")
    analysis = github_analyzer.analyze_repository("https://github.com/user/repo")
    """)


def demo_batch_processing():
    """Demonstrate batch analysis capabilities."""
    
    print("\n\n📦 Batch Processing Demo")
    print("=" * 30)
    
    sample_readmes = [
        ("Project A", "# Project A\n\nA simple utility library.\n\n## Installation\npip install project-a"),
        ("Project B", "# Project B\n\nComprehensive documentation with examples.\n\n## Features\n- Feature 1\n- Feature 2\n\n## Installation\n```bash\nnpm install project-b\n```\n\n## Usage\n```javascript\nconst project = require('project-b');\nproject.run();\n```"),
        ("Project C", "# Advanced Analytics Platform\n\nA sophisticated platform for enterprise data analytics with machine learning capabilities, comprehensive API documentation, and extensive integration options for modern cloud infrastructure deployments.\n\n## Architecture Overview\n\nThe platform utilizes distributed computing paradigms with microservices architecture to ensure scalability and maintainability across heterogeneous environments.")
    ]
    
    analyzer = ReadmeAnalyzer()
    results = []
    
    print("📊 Analyzing multiple README samples...")
    
    for name, content in sample_readmes:
        analysis = analyzer.analyze_content(content, readme_path=f"{name}/README.md")
        results.append((name, analysis))
        print(f"  ✅ {name}: {analysis.quality.overall_score:.1f}/100 ({analysis.quality.grade_level})")
    
    # Calculate batch statistics
    scores = [analysis.quality.overall_score for _, analysis in results]
    avg_score = sum(scores) / len(scores)
    
    print(f"\n📈 Batch Summary:")
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"  Best: {max(scores):.1f}/100")
    print(f"  Worst: {min(scores):.1f}/100")
    print(f"  Range: {max(scores) - min(scores):.1f} points")


def demo_analysis_summary():
    """Demonstrate analysis summary functionality."""
    
    print("\n\n📋 Analysis Summary Demo")
    print("=" * 30)
    
    analyzer = ReadmeAnalyzer()
    
    # Analyze our own README
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        print(f"📖 Analyzing platform's own README: {readme_path}")
        
        analysis = analyzer.analyze_file(str(readme_path))
        summary = analyzer.get_analysis_summary(analysis)
        
        print("\n📊 Summary Report:")
        for key, value in summary.items():
            if key not in ['top_recommendations', 'strengths', 'improvement_areas']:
                print(f"  {key}: {value}")
        
        print("\n🎯 Top Recommendations:")
        for rec in summary.get('top_recommendations', []):
            print(f"  • {rec}")
    else:
        print("ℹ️  Platform README not found - using sample content")


def main():
    """Main demo function."""
    
    try:
        # Run all demos
        demo_basic_analysis()
        demo_custom_weights()
        demo_github_integration()
        demo_batch_processing()
        demo_analysis_summary()
        
        print("\n\n🎉 Demo completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Try the CLI: readme-analyzer README.md")
        print("  2. Start the API server: readme-server")
        print("  3. Launch the web dashboard: readme-dashboard")
        print("  4. Set up GitHub Actions: See github_actions/ directory")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()