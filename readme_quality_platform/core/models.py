"""
Data models for README quality assessment results.

This module defines comprehensive data structures for storing and analyzing
README quality metrics across multiple dimensions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json


@dataclass
class ReadabilityMetrics:
    """
    Comprehensive readability assessment using established linguistic formulas.
    
    Based on traditional readability formulas adapted for technical documentation:
    - Flesch Reading Ease (1948): 0-100 scale, higher = more readable
    - Flesch-Kincaid Grade Level (1975): US education grade level
    - Gunning Fog Index (1952): Years of schooling required
    - SMOG Index (1969): Polysyllable-based complexity
    - Dale-Chall Readability Score (1948): Familiar word ratio analysis
    - Automated Readability Index (1967): Character/word/sentence ratios
    """
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    smog_index: float = 0.0
    dale_chall: float = 0.0
    automated_readability_index: float = 0.0
    
    # Additional metrics
    coleman_liau: float = 0.0
    linsear_write: float = 0.0
    
    # Text statistics
    sentence_count: int = 0
    word_count: int = 0
    character_count: int = 0
    syllable_count: int = 0
    polysyllable_count: int = 0
    
    # Composite scores
    average_grade_level: float = 0.0
    readability_consensus: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'flesch_reading_ease': self.flesch_reading_ease,
            'flesch_kincaid_grade': self.flesch_kincaid_grade,
            'gunning_fog': self.gunning_fog,
            'smog_index': self.smog_index,
            'dale_chall': self.dale_chall,
            'automated_readability_index': self.automated_readability_index,
            'coleman_liau': self.coleman_liau,
            'linsear_write': self.linsear_write,
            'sentence_count': self.sentence_count,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'syllable_count': self.syllable_count,
            'polysyllable_count': self.polysyllable_count,
            'average_grade_level': self.average_grade_level,
            'readability_consensus': self.readability_consensus,
        }


@dataclass
class StructuralMetrics:
    """
    Structural integrity assessment of README organization and completeness.
    
    Evaluates presence and quality of essential documentation sections
    according to conventional documentation patterns.
    """
    # Essential sections presence (boolean flags)
    has_title: bool = False
    has_description: bool = False
    has_installation: bool = False
    has_usage: bool = False
    has_examples: bool = False
    has_api_docs: bool = False
    has_contributing: bool = False
    has_license: bool = False
    has_changelog: bool = False
    has_badges: bool = False
    has_toc: bool = False
    
    # Section quality scores (0-100)
    title_quality: float = 0.0
    description_quality: float = 0.0
    installation_quality: float = 0.0
    usage_quality: float = 0.0
    examples_quality: float = 0.0
    
    # Hierarchical structure
    heading_levels: List[int] = field(default_factory=list)
    max_heading_depth: int = 0
    heading_consistency: float = 0.0
    
    # Organization metrics
    section_count: int = 0
    completeness_score: float = 0.0
    organization_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'has_title': self.has_title,
            'has_description': self.has_description,
            'has_installation': self.has_installation,
            'has_usage': self.has_usage,
            'has_examples': self.has_examples,
            'has_api_docs': self.has_api_docs,
            'has_contributing': self.has_contributing,
            'has_license': self.has_license,
            'has_changelog': self.has_changelog,
            'has_badges': self.has_badges,
            'has_toc': self.has_toc,
            'title_quality': self.title_quality,
            'description_quality': self.description_quality,
            'installation_quality': self.installation_quality,
            'usage_quality': self.usage_quality,
            'examples_quality': self.examples_quality,
            'heading_levels': self.heading_levels,
            'max_heading_depth': self.max_heading_depth,
            'heading_consistency': self.heading_consistency,
            'section_count': self.section_count,
            'completeness_score': self.completeness_score,
            'organization_score': self.organization_score,
        }


@dataclass
class ComplexityMetrics:
    """
    Document complexity and sophistication analysis.
    
    Quantifies README sophistication through rich formatting elements
    and document structure complexity.
    """
    # Content elements
    code_block_count: int = 0
    inline_code_count: int = 0
    link_count: int = 0
    image_count: int = 0
    table_count: int = 0
    list_count: int = 0
    
    # Formatting richness
    bold_text_count: int = 0
    italic_text_count: int = 0
    strikethrough_count: int = 0
    blockquote_count: int = 0
    
    # Advanced elements
    html_element_count: int = 0
    emoji_count: int = 0
    math_formula_count: int = 0
    
    # Document metrics
    total_lines: int = 0
    markdown_complexity: float = 0.0
    formatting_diversity: float = 0.0
    
    # Composite scores
    complexity_score: float = 0.0
    sophistication_level: str = "basic"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'code_block_count': self.code_block_count,
            'inline_code_count': self.inline_code_count,
            'link_count': self.link_count,
            'image_count': self.image_count,
            'table_count': self.table_count,
            'list_count': self.list_count,
            'bold_text_count': self.bold_text_count,
            'italic_text_count': self.italic_text_count,
            'strikethrough_count': self.strikethrough_count,
            'blockquote_count': self.blockquote_count,
            'html_element_count': self.html_element_count,
            'emoji_count': self.emoji_count,
            'math_formula_count': self.math_formula_count,
            'total_lines': self.total_lines,
            'markdown_complexity': self.markdown_complexity,
            'formatting_diversity': self.formatting_diversity,
            'complexity_score': self.complexity_score,
            'sophistication_level': self.sophistication_level,
        }


@dataclass
class ConsistencyMetrics:
    """
    Code-README consistency analysis.
    
    Measures correlation between repository codebase and README content
    by analyzing class names, methods, and API documentation alignment.
    """
    # Code element extraction
    classes_found: List[str] = field(default_factory=list)
    methods_found: List[str] = field(default_factory=list)
    functions_found: List[str] = field(default_factory=list)
    api_endpoints_found: List[str] = field(default_factory=list)
    
    # Documentation coverage
    classes_documented: List[str] = field(default_factory=list)
    methods_documented: List[str] = field(default_factory=list) 
    functions_documented: List[str] = field(default_factory=list)
    api_endpoints_documented: List[str] = field(default_factory=list)
    
    # Consistency scores (0-100)
    class_consistency: float = 0.0
    method_consistency: float = 0.0
    function_consistency: float = 0.0
    api_consistency: float = 0.0
    
    # Overall metrics
    total_code_elements: int = 0
    documented_elements: int = 0
    consistency_score: float = 0.0
    coverage_ratio: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'classes_found': self.classes_found,
            'methods_found': self.methods_found,
            'functions_found': self.functions_found,
            'api_endpoints_found': self.api_endpoints_found,
            'classes_documented': self.classes_documented,
            'methods_documented': self.methods_documented,
            'functions_documented': self.functions_documented,
            'api_endpoints_documented': self.api_endpoints_documented,
            'class_consistency': self.class_consistency,
            'method_consistency': self.method_consistency,
            'function_consistency': self.function_consistency,
            'api_consistency': self.api_consistency,
            'total_code_elements': self.total_code_elements,
            'documented_elements': self.documented_elements,
            'consistency_score': self.consistency_score,
            'coverage_ratio': self.coverage_ratio,
        }


@dataclass
class QualityScore:
    """
    Comprehensive quality scoring with weighted composite metrics.
    
    Implements multi-dimensional scoring similar to Generate README Eval
    with configurable weightings for different assessment criteria.
    """
    # Individual dimension scores (0-100)
    readability_score: float = 0.0
    structural_score: float = 0.0
    complexity_score: float = 0.0
    consistency_score: float = 0.0
    
    # Weighted composite scores
    overall_score: float = 0.0
    grade_level: str = "F"
    
    # Score breakdown with weights
    weights: Dict[str, float] = field(default_factory=lambda: {
        'readability': 0.25,
        'structural': 0.30,
        'complexity': 0.20,
        'consistency': 0.25,
    })
    
    # Quality indicators
    recommendations: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score."""
        self.overall_score = (
            self.readability_score * self.weights['readability'] +
            self.structural_score * self.weights['structural'] +
            self.complexity_score * self.weights['complexity'] +
            self.consistency_score * self.weights['consistency']
        )
        
        # Assign letter grade
        if self.overall_score >= 90:
            self.grade_level = "A+"
        elif self.overall_score >= 85:
            self.grade_level = "A"
        elif self.overall_score >= 80:
            self.grade_level = "A-"
        elif self.overall_score >= 75:
            self.grade_level = "B+"
        elif self.overall_score >= 70:
            self.grade_level = "B"
        elif self.overall_score >= 65:
            self.grade_level = "B-"
        elif self.overall_score >= 60:
            self.grade_level = "C+"
        elif self.overall_score >= 55:
            self.grade_level = "C"
        elif self.overall_score >= 50:
            self.grade_level = "C-"
        elif self.overall_score >= 45:
            self.grade_level = "D+"
        elif self.overall_score >= 40:
            self.grade_level = "D"
        else:
            self.grade_level = "F"
        
        return self.overall_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'readability_score': self.readability_score,
            'structural_score': self.structural_score,
            'complexity_score': self.complexity_score,
            'consistency_score': self.consistency_score,
            'overall_score': self.overall_score,
            'grade_level': self.grade_level,
            'weights': self.weights,
            'recommendations': self.recommendations,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
        }


@dataclass
class ReadmeAnalysis:
    """
    Complete README analysis results container.
    
    Aggregates all analytical dimensions into a comprehensive assessment
    suitable for reporting, API responses, and further processing.
    """
    # Metadata
    repository_url: Optional[str] = None
    readme_path: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    analyzer_version: str = "1.0.0"
    
    # File characteristics
    file_size_bytes: int = 0
    encoding: str = "utf-8"
    is_valid_markdown: bool = True
    
    # Analysis results
    readability: ReadabilityMetrics = field(default_factory=ReadabilityMetrics)
    structure: StructuralMetrics = field(default_factory=StructuralMetrics)
    complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    consistency: ConsistencyMetrics = field(default_factory=ConsistencyMetrics)
    quality: QualityScore = field(default_factory=QualityScore)
    
    # Processing metadata
    analysis_duration_ms: float = 0.0
    error_messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete analysis to dictionary."""
        return {
            'metadata': {
                'repository_url': self.repository_url,
                'readme_path': self.readme_path,
                'analysis_timestamp': self.analysis_timestamp.isoformat(),
                'analyzer_version': self.analyzer_version,
                'file_size_bytes': self.file_size_bytes,
                'encoding': self.encoding,
                'is_valid_markdown': self.is_valid_markdown,
                'analysis_duration_ms': self.analysis_duration_ms,
            },
            'readability': self.readability.to_dict(),
            'structure': self.structure.to_dict(),
            'complexity': self.complexity.to_dict(),
            'consistency': self.consistency.to_dict(),
            'quality': self.quality.to_dict(),
            'error_messages': self.error_messages,
            'warnings': self.warnings,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def save_to_file(self, filepath: str) -> None:
        """Save analysis results to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReadmeAnalysis':
        """Create ReadmeAnalysis from dictionary."""
        metadata = data.get('metadata', {})
        
        analysis = cls(
            repository_url=metadata.get('repository_url'),
            readme_path=metadata.get('readme_path', ''),
            analyzer_version=metadata.get('analyzer_version', '1.0.0'),
            file_size_bytes=metadata.get('file_size_bytes', 0),
            encoding=metadata.get('encoding', 'utf-8'),
            is_valid_markdown=metadata.get('is_valid_markdown', True),
            analysis_duration_ms=metadata.get('analysis_duration_ms', 0.0),
            error_messages=data.get('error_messages', []),
            warnings=data.get('warnings', []),
        )
        
        # Parse timestamp
        if 'analysis_timestamp' in metadata:
            analysis.analysis_timestamp = datetime.fromisoformat(
                metadata['analysis_timestamp']
            )
        
        return analysis