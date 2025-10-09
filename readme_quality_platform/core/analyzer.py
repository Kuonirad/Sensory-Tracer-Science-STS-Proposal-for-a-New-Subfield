"""
Main README Quality Analyzer

Orchestrates comprehensive README analysis across all dimensions:
readability, structural integrity, complexity, and code consistency.
Implements weighted composite scoring similar to Generate README Eval.
"""

import time
from typing import Optional, Dict, Any
from pathlib import Path

from .models import ReadmeAnalysis, QualityScore
from ..metrics import (
    ReadabilityAnalyzer, 
    StructuralAnalyzer,
    ComplexityAnalyzer,
    ConsistencyAnalyzer
)


class ReadmeAnalyzer:
    """
    Comprehensive README quality analyzer.
    
    Coordinates analysis across multiple dimensions and produces
    weighted composite quality scores with detailed recommendations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Optional configuration dictionary for scoring weights
                   and analysis parameters
        """
        self.config = config or {}
        
        # Initialize specialized analyzers
        self.readability_analyzer = ReadabilityAnalyzer()
        self.structural_analyzer = StructuralAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.consistency_analyzer = ConsistencyAnalyzer()
        
        # Configure scoring weights (can be overridden via config)
        self.scoring_weights = self.config.get('scoring_weights', {
            'readability': 0.25,
            'structural': 0.30,
            'complexity': 0.20,
            'consistency': 0.25,
        })
        
        # Quality thresholds for recommendations
        self.thresholds = self.config.get('thresholds', {
            'excellent': 90,
            'good': 75,
            'fair': 60,
            'poor': 45,
        })
    
    def analyze_file(self, file_path: str, repository_path: str = None) -> ReadmeAnalysis:
        """
        Analyze a README file from filesystem.
        
        Args:
            file_path: Path to README file
            repository_path: Optional path to repository for consistency analysis
            
        Returns:
            ReadmeAnalysis: Complete analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file info
            file_info = Path(file_path).stat()
            
            return self.analyze_content(
                content=content,
                readme_path=file_path,
                repository_path=repository_path,
                file_size_bytes=file_info.st_size
            )
            
        except Exception as e:
            # Return analysis with error
            analysis = ReadmeAnalysis(
                readme_path=file_path,
                error_messages=[f"Failed to read file: {str(e)}"]
            )
            return analysis
    
    def analyze_content(self, 
                       content: str,
                       readme_path: str = "",
                       repository_path: str = None,
                       repository_url: str = None,
                       file_size_bytes: int = None) -> ReadmeAnalysis:
        """
        Analyze README content directly.
        
        Args:
            content: README text content
            readme_path: Path to README file (for reference)
            repository_path: Optional path to repository for consistency analysis
            repository_url: Optional repository URL for GitHub integration
            file_size_bytes: Optional file size information
            
        Returns:
            ReadmeAnalysis: Complete analysis results
        """
        start_time = time.time()
        
        # Initialize analysis result
        analysis = ReadmeAnalysis(
            readme_path=readme_path,
            repository_url=repository_url,
            file_size_bytes=file_size_bytes or len(content.encode('utf-8'))
        )
        
        try:
            # Validate content
            if not content.strip():
                analysis.warnings.append("README file is empty")
                analysis.analysis_duration_ms = (time.time() - start_time) * 1000
                return analysis
            
            # Detect encoding issues
            try:
                content.encode('utf-8')
                analysis.encoding = 'utf-8'
            except UnicodeEncodeError:
                analysis.encoding = 'unknown'
                analysis.warnings.append("Encoding issues detected")
            
            # Check if content is valid markdown (basic check)
            analysis.is_valid_markdown = self._validate_markdown(content)
            if not analysis.is_valid_markdown:
                analysis.warnings.append("Content may not be valid markdown")
            
            # Perform multi-dimensional analysis
            self._run_readability_analysis(content, analysis)
            self._run_structural_analysis(content, analysis)  
            self._run_complexity_analysis(content, analysis)
            self._run_consistency_analysis(content, repository_path, analysis)
            
            # Calculate composite quality score
            self._calculate_quality_score(analysis)
            
            # Generate recommendations
            self._generate_recommendations(analysis)
            
        except Exception as e:
            analysis.error_messages.append(f"Analysis error: {str(e)}")
        
        # Record analysis duration
        analysis.analysis_duration_ms = (time.time() - start_time) * 1000
        
        return analysis
    
    def _validate_markdown(self, content: str) -> bool:
        """Basic markdown validation."""
        # Check for common markdown indicators
        markdown_indicators = [
            r'^#{1,6}\s',      # Headers
            r'\[.*\]\(.*\)',   # Links  
            r'!\[.*\]\(.*\)',  # Images
            r'```',            # Code blocks
            r'^\s*[-*+]\s',    # Lists
            r'^\s*\d+\.\s',    # Numbered lists
        ]
        
        import re
        for pattern in markdown_indicators:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        # If no markdown found but content exists, still consider valid
        # (could be plain text README)
        return True
    
    def _run_readability_analysis(self, content: str, analysis: ReadmeAnalysis) -> None:
        """Perform readability analysis."""
        try:
            analysis.readability = self.readability_analyzer.analyze(content)
        except Exception as e:
            analysis.warnings.append(f"Readability analysis failed: {str(e)}")
    
    def _run_structural_analysis(self, content: str, analysis: ReadmeAnalysis) -> None:
        """Perform structural analysis."""
        try:
            analysis.structure = self.structural_analyzer.analyze(content)
        except Exception as e:
            analysis.warnings.append(f"Structural analysis failed: {str(e)}")
    
    def _run_complexity_analysis(self, content: str, analysis: ReadmeAnalysis) -> None:
        """Perform complexity analysis."""
        try:
            analysis.complexity = self.complexity_analyzer.analyze(content)
        except Exception as e:
            analysis.warnings.append(f"Complexity analysis failed: {str(e)}")
    
    def _run_consistency_analysis(self, content: str, repository_path: str, analysis: ReadmeAnalysis) -> None:
        """Perform consistency analysis."""
        try:
            analysis.consistency = self.consistency_analyzer.analyze(
                content, repository_path
            )
        except Exception as e:
            analysis.warnings.append(f"Consistency analysis failed: {str(e)}")
    
    def _calculate_quality_score(self, analysis: ReadmeAnalysis) -> None:
        """Calculate comprehensive quality score."""
        quality = QualityScore()
        
        # Calculate individual dimension scores (0-100)
        quality.readability_score = self._calculate_readability_score(analysis.readability)
        quality.structural_score = self._calculate_structural_score(analysis.structure)
        quality.complexity_score = self._calculate_complexity_score(analysis.complexity)
        quality.consistency_score = self._calculate_consistency_score(analysis.consistency)
        
        # Set custom weights if provided
        if 'scoring_weights' in self.config:
            quality.weights = self.config['scoring_weights']
        else:
            quality.weights = self.scoring_weights
        
        # Calculate weighted overall score
        quality.calculate_overall_score()
        
        analysis.quality = quality
    
    def _calculate_readability_score(self, readability) -> float:
        """Convert readability metrics to 0-100 score."""
        if readability.word_count == 0:
            return 0.0
        
        # Base score on Flesch Reading Ease (already 0-100)
        base_score = max(0, min(100, readability.flesch_reading_ease))
        
        # Adjust based on consensus and grade level appropriateness
        consensus_adjustments = {
            'very easy': 5,      # Bonus for accessibility
            'easy': 10,          # Good for most users
            'fairly easy': 15,   # Optimal for documentation
            'standard': 10,      # Good balance
            'fairly difficult': 0,  # Neutral
            'difficult': -10,    # Penalty for complexity
            'very difficult': -20,  # Significant penalty
        }
        
        adjustment = consensus_adjustments.get(readability.readability_consensus, 0)
        
        # Grade level penalty (technical docs should be accessible)
        if readability.average_grade_level > 16:
            adjustment -= 15
        elif readability.average_grade_level > 12:
            adjustment -= 5
        
        final_score = base_score + adjustment
        return max(0, min(100, final_score))
    
    def _calculate_structural_score(self, structure) -> float:
        """Convert structural metrics to 0-100 score."""
        # Weighted combination of completeness and organization
        completeness_weight = 0.7
        organization_weight = 0.3
        
        score = (structure.completeness_score * completeness_weight +
                structure.organization_score * organization_weight)
        
        return max(0, min(100, score))
    
    def _calculate_complexity_score(self, complexity) -> float:
        """Convert complexity metrics to 0-100 score."""
        # Complexity score is already calculated in the analyzer
        # but we may want to adjust it based on document length and type
        
        base_score = complexity.complexity_score
        
        # Adjust based on sophistication level
        sophistication_bonuses = {
            'minimal': -10,      # Too simple
            'basic': 0,          # Adequate
            'intermediate': 10,   # Good balance
            'advanced': 15,      # Comprehensive
            'expert': 20,        # Exceptional
        }
        
        bonus = sophistication_bonuses.get(complexity.sophistication_level, 0)
        
        final_score = base_score + bonus
        return max(0, min(100, final_score))
    
    def _calculate_consistency_score(self, consistency) -> float:
        """Convert consistency metrics to 0-100 score."""
        # Use the calculated consistency score directly
        return consistency.consistency_score
    
    def _generate_recommendations(self, analysis: ReadmeAnalysis) -> None:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        strengths = []
        weaknesses = []
        
        # Analyze each dimension for recommendations
        self._analyze_readability_recommendations(analysis, recommendations, strengths, weaknesses)
        self._analyze_structural_recommendations(analysis, recommendations, strengths, weaknesses)
        self._analyze_complexity_recommendations(analysis, recommendations, strengths, weaknesses)
        self._analyze_consistency_recommendations(analysis, recommendations, strengths, weaknesses)
        
        # Set recommendations on quality score
        analysis.quality.recommendations = recommendations
        analysis.quality.strengths = strengths
        analysis.quality.weaknesses = weaknesses
    
    def _analyze_readability_recommendations(self, analysis, recommendations, strengths, weaknesses):
        """Generate readability-specific recommendations."""
        readability = analysis.readability
        
        if readability.flesch_reading_ease > 70:
            strengths.append("Excellent readability - accessible to broad audience")
        elif readability.flesch_reading_ease < 30:
            weaknesses.append("Very difficult to read - consider simplifying language")
            recommendations.append("Simplify complex sentences and reduce technical jargon")
        
        if readability.average_grade_level > 16:
            recommendations.append("Consider reducing technical complexity for better accessibility")
        
        if readability.sentence_count > 0 and readability.word_count / readability.sentence_count > 25:
            recommendations.append("Break up long sentences for improved readability")
        
        if readability.word_count < 100:
            recommendations.append("Consider expanding content - README appears quite brief")
        elif readability.word_count > 5000:
            recommendations.append("Consider organizing content with better structure or splitting into multiple documents")
    
    def _analyze_structural_recommendations(self, analysis, recommendations, strengths, weaknesses):
        """Generate structure-specific recommendations."""
        structure = analysis.structure
        
        if structure.completeness_score > 80:
            strengths.append("Comprehensive documentation with all essential sections")
        elif structure.completeness_score < 50:
            weaknesses.append("Missing essential documentation sections")
            
        # Specific section recommendations
        if not structure.has_installation:
            recommendations.append("Add installation instructions for better user onboarding")
        
        if not structure.has_usage:
            recommendations.append("Add usage examples to help users get started")
        
        if not structure.has_examples and structure.has_usage:
            recommendations.append("Consider adding more detailed examples")
        
        if structure.section_count > 15:
            recommendations.append("Consider adding table of contents for better navigation")
        
        if structure.heading_consistency < 70:
            recommendations.append("Improve heading hierarchy consistency (avoid skipping levels)")
    
    def _analyze_complexity_recommendations(self, analysis, recommendations, strengths, weaknesses):
        """Generate complexity-specific recommendations."""
        complexity = analysis.complexity
        
        if complexity.sophistication_level == 'expert':
            strengths.append("Rich formatting with advanced documentation features")
        elif complexity.sophistication_level == 'minimal':
            weaknesses.append("Very basic formatting - consider enriching with examples and visuals")
        
        if complexity.code_block_count == 0:
            recommendations.append("Add code examples to demonstrate usage")
        
        if complexity.image_count == 0 and complexity.total_lines > 50:
            recommendations.append("Consider adding diagrams or screenshots to enhance understanding")
        
        if complexity.link_count < 3:
            recommendations.append("Add relevant links to documentation, resources, or related projects")
        
        if complexity.list_count == 0:
            recommendations.append("Use lists to organize information more clearly")
    
    def _analyze_consistency_recommendations(self, analysis, recommendations, strengths, weaknesses):
        """Generate consistency-specific recommendations."""
        consistency = analysis.consistency
        
        if consistency.consistency_score > 80:
            strengths.append("Good alignment between code and documentation")
        elif consistency.consistency_score < 40:
            weaknesses.append("Poor code-documentation alignment")
        
        if consistency.total_code_elements > 0:
            if consistency.coverage_ratio < 0.3:
                recommendations.append("Document more code elements (classes, functions, APIs) in README")
            
            if len(consistency.api_endpoints_found) > 0 and consistency.api_consistency < 50:
                recommendations.append("Add API endpoint documentation with examples")
        
        if len(consistency.classes_found) > 5 and consistency.class_consistency < 60:
            recommendations.append("Document main classes and their purposes")
    
    def get_analysis_summary(self, analysis: ReadmeAnalysis) -> Dict[str, Any]:
        """
        Get a concise summary of the analysis results.
        
        Args:
            analysis: Complete analysis results
            
        Returns:
            Dictionary with summary metrics and recommendations
        """
        return {
            'overall_score': analysis.quality.overall_score,
            'grade': analysis.quality.grade_level,
            'dimension_scores': {
                'readability': analysis.quality.readability_score,
                'structure': analysis.quality.structural_score,
                'complexity': analysis.quality.complexity_score,
                'consistency': analysis.quality.consistency_score,
            },
            'key_metrics': {
                'word_count': analysis.readability.word_count,
                'readability_level': analysis.readability.readability_consensus,
                'sections_present': analysis.structure.section_count,
                'completeness': analysis.structure.completeness_score,
                'sophistication': analysis.complexity.sophistication_level,
                'code_coverage': analysis.consistency.coverage_ratio,
            },
            'top_recommendations': analysis.quality.recommendations[:3],
            'strengths': analysis.quality.strengths,
            'improvement_areas': analysis.quality.weaknesses,
            'analysis_time': analysis.analysis_duration_ms,
        }