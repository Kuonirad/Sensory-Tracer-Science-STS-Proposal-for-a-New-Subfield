"""
Structural Integrity Analysis for README Files

Comprehensive evaluation of README organization, completeness, and adherence
to conventional documentation patterns. Analyzes section presence, quality,
and hierarchical coherence.
"""

import re
from typing import List, Dict, Tuple, Set, Optional
from bs4 import BeautifulSoup
import markdown
from markdown.extensions import codehilite, tables, toc

from ..core.models import StructuralMetrics


class StructuralAnalyzer:
    """
    Advanced structural analysis for README documentation.
    
    Evaluates presence and organization of essential sections, heading hierarchy,
    content quality indicators, and adherence to documentation best practices.
    """
    
    def __init__(self):
        """Initialize with section patterns and quality indicators."""
        self._define_section_patterns()
        self._define_quality_indicators()
    
    def _define_section_patterns(self) -> None:
        """Define regex patterns for identifying common README sections."""
        self.section_patterns = {
            'title': [
                r'^#\s+(.+)',  # Main heading
                r'<h1[^>]*>(.+?)</h1>',  # HTML h1
            ],
            'description': [
                r'(?i)(?:^|\n)#{1,2}\s*(?:description|about|overview|what\s+is|introduction).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:^|\n)(?:description|about|overview|what\s+is|introduction):\s*(.*?)(?=\n\n|\n[A-Z]|\Z)',
            ],
            'installation': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:installation|install|setup|getting\s+started|quick\s+start).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:npm\s+install|pip\s+install|yarn\s+add|go\s+get|composer\s+require)',
            ],
            'usage': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:usage|how\s+to\s+use|example|examples|basic\s+usage).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)```(?:javascript|python|bash|sh|shell)',
            ],
            'examples': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:examples?|demo|sample).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'```[\s\S]*?```',  # Code blocks as examples
            ],
            'api_docs': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:api|reference|documentation|methods|functions|endpoints).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:class|function|method|endpoint|route):',
            ],
            'contributing': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:contributing|contribution|development|developers?).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:pull\s+request|bug\s+report|contribution\s+guidelines)',
            ],
            'license': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:license|licensing).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:mit|apache|gpl|bsd|creative\s+commons|cc)',
            ],
            'changelog': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:changelog|changes|history|versions?).*?\n(.*?)(?=\n#|\n\n|\Z)',
                r'(?i)(?:version|v\d+\.\d+\.\d+|\d{4}-\d{2}-\d{2})',
            ],
            'badges': [
                r'\[!\[([^\]]*)\]\([^\)]+\)\]\([^\)]+\)',  # Badge with link
                r'!\[([^\]]*)\]\(https://img\.shields\.io[^\)]+\)',  # Shields.io badges
                r'https://(?:travis-ci|circleci|appveyor|codecov|coveralls)',
            ],
            'toc': [
                r'(?i)(?:^|\n)#{1,3}\s*(?:table\s+of\s+contents|contents|index).*?\n',
                r'\[TOC\]',  # Markdown TOC extension
                r'(?:\*|\-|\+|\d+\.)\s*\[.+?\]\(#.+?\)',  # Manual TOC links
            ],
        }
    
    def _define_quality_indicators(self) -> None:
        """Define patterns that indicate high-quality content in each section."""
        self.quality_indicators = {
            'title': {
                'good': [
                    r'.{10,80}',  # Reasonable length
                    r'[A-Z]',     # Contains uppercase
                ],
                'bad': [
                    r'^untitled$|^readme$|^project$',  # Generic titles
                    r'.{1,5}$',   # Too short
                    r'.{100,}',   # Too long
                ]
            },
            'description': {
                'good': [
                    r'.{50,500}',     # Good length
                    r'(?:what|why|how)', # Explanatory words
                    r'(?:library|framework|tool|application|service)', # Project type
                ],
                'bad': [
                    r'^.{1,20}$',     # Too short
                    r'^todo|^placeholder|^coming\s+soon',  # Placeholder text
                ]
            },
            'installation': {
                'good': [
                    r'(?:npm|pip|yarn|go\s+get|composer|cargo|gem\s+install)', # Package managers
                    r'(?:git\s+clone|download|curl)', # Download methods
                    r'(?:requirements|dependencies|prerequisites)', # Prerequisites
                ],
                'bad': [
                    r'^todo|^coming\s+soon',  # Placeholder
                ]
            },
            'usage': {
                'good': [
                    r'```[\s\S]*?```',  # Code examples
                    r'(?:import|require|include|use)', # Import statements
                    r'(?:example|sample|basic)', # Example indicators
                ],
                'bad': [
                    r'^todo|^coming\s+soon',  # Placeholder
                ]
            },
            'examples': {
                'good': [
                    r'```[\s\S]*?```',  # Multiple code blocks
                    r'(?:output|result|returns)', # Output descriptions
                ],
                'bad': [
                    r'^todo|^coming\s+soon',  # Placeholder
                ]
            }
        }
    
    def analyze(self, text: str) -> StructuralMetrics:
        """
        Perform comprehensive structural analysis of README content.
        
        Args:
            text: Raw README text (markdown)
            
        Returns:
            StructuralMetrics: Complete structural assessment
        """
        metrics = StructuralMetrics()
        
        # Parse markdown to HTML for better analysis
        md = markdown.Markdown(extensions=['codehilite', 'tables', 'toc'])
        html = md.convert(text)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Analyze section presence and content
        self._analyze_sections(text, metrics)
        
        # Analyze heading structure
        self._analyze_heading_structure(text, soup, metrics)
        
        # Calculate quality scores
        self._calculate_section_quality(text, metrics)
        
        # Calculate composite scores
        self._calculate_composite_scores(metrics)
        
        return metrics
    
    def _analyze_sections(self, text: str, metrics: StructuralMetrics) -> None:
        """Detect presence of essential README sections."""
        text_lower = text.lower()
        
        # Check each section type
        for section_name, patterns in self.section_patterns.items():
            section_found = False
            for pattern in patterns:
                if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                    section_found = True
                    break
            
            # Set boolean flags
            setattr(metrics, f'has_{section_name}', section_found)
    
    def _analyze_heading_structure(self, text: str, soup: BeautifulSoup, metrics: StructuralMetrics) -> None:
        """Analyze heading hierarchy and organization."""
        # Extract all headings with their levels
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        headings = re.findall(heading_pattern, text, re.MULTILINE)
        
        if not headings:
            return
        
        heading_levels = [len(level) for level, _ in headings]
        metrics.heading_levels = heading_levels
        metrics.max_heading_depth = max(heading_levels) if heading_levels else 0
        metrics.section_count = len(heading_levels)
        
        # Calculate heading consistency (proper nesting)
        consistency_score = self._calculate_heading_consistency(heading_levels)
        metrics.heading_consistency = consistency_score
    
    def _calculate_heading_consistency(self, levels: List[int]) -> float:
        """Calculate heading hierarchy consistency score (0-100)."""
        if len(levels) <= 1:
            return 100.0
        
        violations = 0
        max_violations = len(levels) - 1
        
        for i in range(1, len(levels)):
            prev_level = levels[i-1]
            curr_level = levels[i]
            
            # Check for proper nesting (no skipping levels down)
            if curr_level > prev_level + 1:
                violations += 1
        
        consistency = (1 - violations / max_violations) * 100
        return max(0, consistency)
    
    def _calculate_section_quality(self, text: str, metrics: StructuralMetrics) -> None:
        """Calculate quality scores for individual sections."""
        section_contents = self._extract_section_contents(text)
        
        for section_name, content in section_contents.items():
            if not content:
                continue
                
            quality_attr = f'{section_name}_quality'
            if hasattr(metrics, quality_attr):
                score = self._score_section_quality(section_name, content)
                setattr(metrics, quality_attr, score)
    
    def _extract_section_contents(self, text: str) -> Dict[str, str]:
        """Extract content for each identified section."""
        sections = {}
        
        # Split text into sections based on headings
        section_pattern = r'^(#{1,6})\s+(.+)$'
        parts = re.split(section_pattern, text, flags=re.MULTILINE)
        
        current_section = None
        current_content = []
        
        for i, part in enumerate(parts):
            if i % 3 == 0:  # Regular text
                if part.strip():
                    current_content.append(part.strip())
            elif i % 3 == 1:  # Heading level
                continue
            else:  # Heading text (i % 3 == 2)
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = self._classify_heading(part)
                current_content = []
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _classify_heading(self, heading_text: str) -> Optional[str]:
        """Classify a heading into a known section type."""
        heading_lower = heading_text.lower()
        
        classification_patterns = {
            'title': [r'title', r'^[^a-z]*$'],  # All caps or symbols
            'description': [r'description', r'about', r'overview', r'what.*is', r'introduction'],
            'installation': [r'install', r'setup', r'getting.*started', r'quick.*start'],
            'usage': [r'usage', r'how.*to.*use', r'basic.*usage'],
            'examples': [r'examples?', r'demo', r'samples?'],
            'api_docs': [r'api', r'reference', r'documentation', r'methods', r'functions'],
            'contributing': [r'contribut', r'development', r'developers?'],
            'license': [r'licens'],
            'changelog': [r'changelog', r'changes', r'history', r'versions?'],
        }
        
        for section_type, patterns in classification_patterns.items():
            for pattern in patterns:
                if re.search(pattern, heading_lower):
                    return section_type
        
        return 'other'
    
    def _score_section_quality(self, section_name: str, content: str) -> float:
        """Score the quality of a specific section's content (0-100)."""
        if section_name not in self.quality_indicators:
            return 50.0  # Default score for unknown sections
        
        indicators = self.quality_indicators[section_name]
        score = 50.0  # Base score
        
        # Check good indicators
        good_matches = 0
        for pattern in indicators.get('good', []):
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                good_matches += 1
        
        # Check bad indicators
        bad_matches = 0
        for pattern in indicators.get('bad', []):
            if re.search(pattern, content, re.IGNORECASE):
                bad_matches += 1
        
        # Calculate score adjustments
        good_bonus = min(25.0, good_matches * 8)  # Up to 25 points for good indicators
        bad_penalty = min(30.0, bad_matches * 15)  # Up to 30 points penalty
        
        # Length bonus (reasonable content length)
        length = len(content.strip())
        if 50 <= length <= 1000:
            length_bonus = 10
        elif 20 <= length <= 2000:
            length_bonus = 5
        else:
            length_bonus = 0
        
        final_score = score + good_bonus - bad_penalty + length_bonus
        return max(0, min(100, final_score))
    
    def _calculate_composite_scores(self, metrics: StructuralMetrics) -> None:
        """Calculate overall completeness and organization scores."""
        # Essential sections for completeness calculation
        essential_sections = [
            'has_title', 'has_description', 'has_installation', 
            'has_usage', 'has_examples'
        ]
        
        # Count present essential sections
        present_count = sum(1 for section in essential_sections 
                          if getattr(metrics, section, False))
        
        # Completeness score (essential sections)
        metrics.completeness_score = (present_count / len(essential_sections)) * 100
        
        # Bonus points for additional sections
        bonus_sections = [
            'has_api_docs', 'has_contributing', 'has_license', 
            'has_changelog', 'has_badges', 'has_toc'
        ]
        
        bonus_count = sum(1 for section in bonus_sections 
                         if getattr(metrics, section, False))
        
        bonus_points = min(15, bonus_count * 2.5)  # Up to 15 bonus points
        metrics.completeness_score = min(100, metrics.completeness_score + bonus_points)
        
        # Organization score (structure quality)
        organization_factors = []
        
        # Heading consistency factor
        if metrics.heading_consistency > 0:
            organization_factors.append(metrics.heading_consistency)
        
        # Appropriate section count factor
        if 3 <= metrics.section_count <= 15:
            section_score = 100
        elif 1 <= metrics.section_count <= 20:
            section_score = 80
        else:
            section_score = 60
        organization_factors.append(section_score)
        
        # TOC presence for large documents
        if metrics.section_count >= 8:
            toc_score = 100 if metrics.has_toc else 70
        else:
            toc_score = 100  # TOC not needed for small docs
        organization_factors.append(toc_score)
        
        # Calculate average organization score
        metrics.organization_score = (
            sum(organization_factors) / len(organization_factors) 
            if organization_factors else 0
        )