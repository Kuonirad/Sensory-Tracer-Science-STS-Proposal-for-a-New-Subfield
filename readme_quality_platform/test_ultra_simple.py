#!/usr/bin/env python3
"""
Test the ultra-simplified README to see if we achieve 100/100 scores.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the working demo components
from demo_working import SimpleReadmeAnalyzer

def test_ultra_simple_readme():
    """Test the ultra-simplified README."""
    
    # Read the ultra-simplified README
    try:
        with open('README_ULTRA_SIMPLE.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ README_ULTRA_SIMPLE.md not found!")
        return
    
    print("🎯 Testing Ultra-Simplified README for Perfect Scores")
    print("=" * 55)
    print(f"📄 File: README_ULTRA_SIMPLE.md")
    print(f"📊 Content length: {len(content)} characters")
    print()
    
    # Initialize analyzer
    analyzer = SimpleReadmeAnalyzer()
    
    # Perform analysis
    print("🔍 Analyzing ultra-simplified README...")
    results = analyzer.analyze(content)
    
    # Display results
    print("\n🎯 SCORE RESULTS")
    print("=" * 20)
    print(f"🏆 Overall Score: {results['overall_score']:.1f}/100")
    print(f"🎖️  Grade: {results['grade']}")
    
    # Check if we hit our targets
    target_met = results['overall_score'] >= 100.0
    status = "🎉 TARGET ACHIEVED!" if target_met else "⚠️  Still needs work"
    print(f"\n{status}")
    
    print("\n📊 Dimension Breakdown")
    print("-" * 25)
    for dimension, score in results['scores'].items():
        target_status = "✅" if score >= 100.0 else "❌" if score < 80.0 else "⚠️"
        if dimension == 'consistency':
            print(f"{target_status} {dimension.title()}: {score:.1f}/100 (placeholder)")
        else:
            print(f"{target_status} {dimension.title()}: {score:.1f}/100")
    
    print(f"\n📖 Readability Details")
    print("-" * 22)
    readability = results['readability']
    print(f"📝 Word Count: {readability.word_count}")
    print(f"📄 Sentences: {readability.sentence_count}")
    print(f"📊 Flesch Reading Ease: {readability.flesch_reading_ease:.1f}")
    print(f"🎓 Grade Level: {readability.flesch_kincaid_grade:.1f}")
    print(f"🌫️  Gunning Fog: {readability.gunning_fog:.1f}")
    print(f"📈 Readability Level: {readability.readability_level}")
    
    print(f"\n🏗️  Structure Details")
    print("-" * 20)
    structure = results['structure']
    print(f"📑 Section Count: {structure.section_count}")
    print(f"✅ Completeness: {structure.completeness_score:.1f}%")
    
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
    
    print(f"\n🔧 Complexity Details")
    print("-" * 21)
    complexity = results['complexity']
    print(f"💻 Code Blocks: {complexity.code_blocks}")
    print(f"🔗 Links: {complexity.links}")
    print(f"🖼️  Images: {complexity.images}")
    print(f"📋 Tables: {complexity.tables}")
    print(f"📝 Lists: {complexity.lists}")
    print(f"**Bold Text**: {complexity.bold_text}")
    print(f"🎯 Total Elements: {complexity.total_elements}")
    print(f"📊 Complexity Score: {complexity.complexity_score:.1f}/100")
    
    # Provide recommendations if not perfect
    if results['overall_score'] < 100.0:
        print(f"\n💡 Recommendations for Perfect Score")
        print("-" * 35)
        
        if results['scores']['readability'] < 100.0:
            print("📖 Readability improvements needed:")
            print("   • Use even simpler words (1-2 syllables)")
            print("   • Make sentences shorter (under 10 words)")
            print("   • Remove technical jargon")
            print("   • Use more common vocabulary")
        
        if results['scores']['structural'] < 100.0:
            print("🏗️  Structure improvements needed:")
            print("   • Add missing essential sections")
            print("   • Improve section organization")
        
        if results['scores']['complexity'] < 100.0:
            print("🔧 Complexity improvements needed:")
            print("   • Add more formatting elements")
            print("   • Include code examples")
            print("   • Add tables and lists")
    
    return results

if __name__ == "__main__":
    test_ultra_simple_readme()