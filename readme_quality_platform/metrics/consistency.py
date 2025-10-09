"""
Code-README Consistency Analysis

Measures correlation between repository codebase and README content by extracting
class names, method signatures, API endpoints, and comparing with documentation
coverage as described in Generate README Eval methodology.
"""

import re
import os
import ast
from typing import List, Dict, Set, Tuple, Optional, Any
from pathlib import Path
import json

from ..core.models import ConsistencyMetrics


class ConsistencyAnalyzer:
    """
    Advanced code-README consistency analysis.
    
    Extracts code elements from multiple programming languages and analyzes
    how well they are documented in the README. Implements correlation
    measurement similar to Generate README Eval benchmarks.
    """
    
    def __init__(self):
        """Initialize with language parsers and pattern matchers."""
        self._define_language_patterns()
        self._define_documentation_patterns()
    
    def _define_language_patterns(self) -> None:
        """Define regex patterns for extracting code elements from different languages."""
        self.language_patterns = {
            'python': {
                'classes': [
                    r'class\s+([A-Z][a-zA-Z0-9_]*)\s*\(',  # Class definitions
                    r'class\s+([A-Z][a-zA-Z0-9_]*)\s*:',   # Class without inheritance
                ],
                'functions': [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Function definitions
                ],
                'methods': [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(self',  # Instance methods
                ],
                'api_endpoints': [
                    r'@app\.route\s*\(\s*[\'"]([^\'"]+)[\'"]',  # Flask routes
                    r'@router\.(get|post|put|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]',  # FastAPI routes
                ],
                'imports': [
                    r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',  # From imports
                    r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',         # Direct imports
                ],
            },
            'javascript': {
                'classes': [
                    r'class\s+([A-Z][a-zA-Z0-9_]*)',  # ES6 classes
                ],
                'functions': [
                    r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',  # Function declarations
                    r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*=>|\w+\s*=>)',  # Arrow functions
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?function',  # Object methods
                ],
                'api_endpoints': [
                    r'app\.(get|post|put|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]',  # Express routes
                    r'router\.(get|post|put|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]',  # Express router
                ],
                'exports': [
                    r'module\.exports\s*=\s*([a-zA-Z_$][a-zA-Z0-9_$]*)',  # CommonJS exports
                    r'export\s+(?:default\s+)?(?:class\s+|function\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)',  # ES6 exports
                ],
            },
            'java': {
                'classes': [
                    r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Z][a-zA-Z0-9_]*)',
                    r'(?:public\s+|private\s+|protected\s+)?interface\s+([A-Z][a-zA-Z0-9_]*)',
                ],
                'methods': [
                    r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?[a-zA-Z<>\[\]_]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                ],
                'api_endpoints': [
                    r'@RequestMapping\s*\(\s*[\'"]([^\'"]+)[\'"]',  # Spring mappings
                    r'@(Get|Post|Put|Delete)Mapping\s*\(\s*[\'"]([^\'"]+)[\'"]',
                ],
            },
            'go': {
                'functions': [
                    r'func\s+([A-Z][a-zA-Z0-9_]*)\s*\(',  # Exported functions (capitalized)
                ],
                'types': [
                    r'type\s+([A-Z][a-zA-Z0-9_]*)\s+(?:struct|interface)',  # Exported types
                ],
                'api_endpoints': [
                    r'http\.HandleFunc\s*\(\s*[\'"]([^\'"]+)[\'"]',  # HTTP handlers
                    r'r\.HandleFunc\s*\(\s*[\'"]([^\'"]+)[\'"]',     # Gorilla mux
                ],
            },
            'rust': {
                'functions': [
                    r'pub\s+fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Public functions
                ],
                'structs': [
                    r'pub\s+struct\s+([A-Z][a-zA-Z0-9_]*)',  # Public structs
                ],
                'traits': [
                    r'pub\s+trait\s+([A-Z][a-zA-Z0-9_]*)',   # Public traits
                ],
            },
            'csharp': {
                'classes': [
                    r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Z][a-zA-Z0-9_]*)',
                    r'(?:public\s+|private\s+|protected\s+)?interface\s+([A-Z][a-zA-Z0-9_]*)',
                ],
                'methods': [
                    r'(?:public|private|protected)\s+(?:static\s+)?(?:virtual\s+)?[a-zA-Z<>\[\]_]+\s+([A-Z][a-zA-Z0-9_]*)\s*\(',
                ],
                'api_endpoints': [
                    r'\[Route\s*\(\s*[\'"]([^\'"]+)[\'"]',  # ASP.NET Core routes
                    r'\[Http(Get|Post|Put|Delete)\s*(?:\(\s*[\'"]([^\'"]+)[\'"])?',
                ],
            }
        }
    
    def _define_documentation_patterns(self) -> None:
        """Define patterns for finding documented elements in README."""
        self.doc_patterns = {
            'code_mentions': [
                r'`([a-zA-Z_][a-zA-Z0-9_]*)`',  # Inline code mentions
            ],
            'code_blocks_with_names': [
                r'```[\w]*\s*\n[\s\S]*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([\s\S]*?```',  # Function calls in code blocks
                r'```[\w]*\s*\n[\s\S]*?class\s+([a-zA-Z_][a-zA-Z0-9_]*)[\s\S]*?```',  # Class definitions in code blocks
                r'```[\w]*\s*\n[\s\S]*?([a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*)[\s\S]*?```',  # Method calls
            ],
            'api_documentation': [
                r'(?:GET|POST|PUT|DELETE|PATCH)\s+([/a-zA-Z0-9_{}:-]+)',  # HTTP endpoints
                r'(?:endpoint|route):\s*[\'"`]([/a-zA-Z0-9_{}:-]+)[\'"`]',  # Documented endpoints
            ],
            'section_headers': [
                r'#{1,6}\s+.*?([A-Z][a-zA-Z0-9_]*)',  # Class/function names in headers
            ],
            'direct_mentions': [
                r'\b([A-Z][a-zA-Z0-9_]*)\b',  # Direct mentions of capitalized names
            ]
        }
    
    def analyze(self, readme_text: str, repository_path: str = None) -> ConsistencyMetrics:
        """
        Perform comprehensive code-README consistency analysis.
        
        Args:
            readme_text: README content to analyze
            repository_path: Path to repository for code analysis (optional)
            
        Returns:
            ConsistencyMetrics: Complete consistency assessment
        """
        metrics = ConsistencyMetrics()
        
        # Extract documented elements from README
        documented_elements = self._extract_documented_elements(readme_text)
        
        # If repository path provided, extract code elements
        if repository_path and os.path.exists(repository_path):
            code_elements = self._extract_code_elements(repository_path)
        else:
            # Create empty code elements structure
            code_elements = {
                'classes': set(),
                'methods': set(),
                'functions': set(),
                'api_endpoints': set(),
            }
        
        # Populate metrics with findings
        self._populate_metrics(metrics, code_elements, documented_elements)
        
        # Calculate consistency scores
        self._calculate_consistency_scores(metrics)
        
        return metrics
    
    def _extract_documented_elements(self, readme_text: str) -> Dict[str, Set[str]]:
        """Extract all code-related elements mentioned in the README."""
        documented = {
            'classes': set(),
            'methods': set(),
            'functions': set(),
            'api_endpoints': set(),
        }
        
        # Extract inline code mentions
        inline_code_pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*)`'
        inline_mentions = re.findall(inline_code_pattern, readme_text)
        
        # Extract from code blocks
        code_block_pattern = r'```[\w]*\s*\n([\s\S]*?)```'
        code_blocks = re.findall(code_block_pattern, readme_text)
        
        # Analyze each code block
        for block in code_blocks:
            # Look for function/method calls
            function_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', block)
            documented['functions'].update(function_calls)
            
            # Look for class instantiations
            class_instantiations = re.findall(r'([A-Z][a-zA-Z0-9_]*)\s*\(', block)
            documented['classes'].update(class_instantiations)
            
            # Look for method calls
            method_calls = re.findall(r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', block)
            documented['methods'].update(method_calls)
        
        # Extract API endpoints
        api_patterns = [
            r'(?:GET|POST|PUT|DELETE|PATCH)\s+([/a-zA-Z0-9_{}:-]+)',
            r'(?:endpoint|route):\s*[\'"`]([/a-zA-Z0-9_{}:-]+)[\'"`]',
            r'/api/([a-zA-Z0-9_/-]+)',
        ]
        
        for pattern in api_patterns:
            endpoints = re.findall(pattern, readme_text, re.IGNORECASE)
            documented['api_endpoints'].update(endpoints)
        
        # Extract from inline code mentions (classify by naming convention)
        for mention in inline_mentions:
            if mention[0].isupper():  # Likely a class name
                documented['classes'].add(mention)
            elif mention.islower() or '_' in mention:  # Likely a function/method
                documented['functions'].add(mention)
        
        # Look for direct mentions in text (be more selective to avoid false positives)
        # Only look for well-known patterns in specific contexts
        class_context_pattern = r'(?:class|object|instance|type)\s+`?([A-Z][a-zA-Z0-9_]*)`?'
        class_mentions = re.findall(class_context_pattern, readme_text, re.IGNORECASE)
        documented['classes'].update(class_mentions)
        
        function_context_pattern = r'(?:function|method|call|invoke)\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?'
        function_mentions = re.findall(function_context_pattern, readme_text, re.IGNORECASE)
        documented['functions'].update(function_mentions)
        
        return documented
    
    def _extract_code_elements(self, repository_path: str) -> Dict[str, Set[str]]:
        """Extract code elements from repository files."""
        code_elements = {
            'classes': set(),
            'methods': set(),
            'functions': set(),
            'api_endpoints': set(),
        }
        
        # Find all source files
        source_files = self._find_source_files(repository_path)
        
        # Analyze each file
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Determine language and extract elements
                language = self._detect_language(file_path)
                if language in self.language_patterns:
                    file_elements = self._extract_from_file(content, language)
                    
                    # Merge with overall results
                    for element_type, elements in file_elements.items():
                        code_elements[element_type].update(elements)
                        
            except Exception as e:
                # Skip files that can't be read
                continue
        
        return code_elements
    
    def _find_source_files(self, repository_path: str) -> List[str]:
        """Find all source code files in the repository."""
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',  # Python, JavaScript, TypeScript
            '.java', '.kt',                        # Java, Kotlin
            '.go',                                 # Go
            '.rs',                                 # Rust  
            '.cs',                                 # C#
            '.cpp', '.cc', '.cxx', '.c', '.h',    # C/C++
            '.rb',                                 # Ruby
            '.php',                                # PHP
            '.swift',                              # Swift
        }
        
        source_files = []
        
        for root, dirs, files in os.walk(repository_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', '.pytest_cache',
                'venv', 'env', '.env', 'build', 'dist', 'target',
                '.idea', '.vscode', 'coverage', '.coverage'
            }]
            
            for file in files:
                if Path(file).suffix.lower() in source_extensions:
                    source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',  # TypeScript uses similar patterns
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.kt': 'java',  # Kotlin uses similar patterns
            '.go': 'go',
            '.rs': 'rust',
            '.cs': 'csharp',
        }
        
        return language_map.get(extension)
    
    def _extract_from_file(self, content: str, language: str) -> Dict[str, Set[str]]:
        """Extract code elements from a single file based on language."""
        elements = {
            'classes': set(),
            'methods': set(),
            'functions': set(),
            'api_endpoints': set(),
        }
        
        if language not in self.language_patterns:
            return elements
        
        patterns = self.language_patterns[language]
        
        # Extract each element type
        for element_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                if element_type == 'api_endpoints':
                    # Special handling for API endpoints (may have tuples)
                    for match in matches:
                        if isinstance(match, tuple):
                            elements[element_type].add(match[1] if len(match) > 1 else match[0])
                        else:
                            elements[element_type].add(match)
                else:
                    # Regular element extraction
                    if element_type in ['classes', 'types', 'structs', 'traits']:
                        elements['classes'].update(matches)
                    elif element_type in ['functions', 'exports']:
                        elements['functions'].update(matches)
                    elif element_type == 'methods':
                        elements['methods'].update(matches)
        
        # For Python, try AST parsing for more accurate extraction
        if language == 'python':
            try:
                ast_elements = self._extract_python_ast(content)
                for element_type, ast_matches in ast_elements.items():
                    elements[element_type].update(ast_matches)
            except:
                pass  # Fall back to regex if AST parsing fails
        
        return elements
    
    def _extract_python_ast(self, content: str) -> Dict[str, Set[str]]:
        """Extract Python elements using AST parsing for higher accuracy."""
        elements = {
            'classes': set(),
            'methods': set(),
            'functions': set(),
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    elements['classes'].add(node.name)
                    
                    # Extract methods from class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            elements['methods'].add(item.name)
                            
                elif isinstance(node, ast.FunctionDef):
                    # Top-level functions
                    elements['functions'].add(node.name)
                    
        except SyntaxError:
            pass  # File has syntax errors, skip AST parsing
        
        return elements
    
    def _populate_metrics(self, 
                         metrics: ConsistencyMetrics, 
                         code_elements: Dict[str, Set[str]], 
                         documented_elements: Dict[str, Set[str]]) -> None:
        """Populate metrics with extracted elements and documented coverage."""
        
        # Store found elements
        metrics.classes_found = list(code_elements['classes'])
        metrics.methods_found = list(code_elements['methods'])
        metrics.functions_found = list(code_elements['functions'])
        metrics.api_endpoints_found = list(code_elements['api_endpoints'])
        
        # Store documented elements
        metrics.classes_documented = list(documented_elements['classes'])
        metrics.methods_documented = list(documented_elements['methods'])
        metrics.functions_documented = list(documented_elements['functions'])
        metrics.api_endpoints_documented = list(documented_elements['api_endpoints'])
        
        # Calculate totals
        metrics.total_code_elements = (
            len(code_elements['classes']) +
            len(code_elements['methods']) +
            len(code_elements['functions']) +
            len(code_elements['api_endpoints'])
        )
        
        metrics.documented_elements = (
            len(documented_elements['classes']) +
            len(documented_elements['methods']) +
            len(documented_elements['functions']) +
            len(documented_elements['api_endpoints'])
        )
    
    def _calculate_consistency_scores(self, metrics: ConsistencyMetrics) -> None:
        """Calculate consistency scores for each element type and overall."""
        
        # Calculate individual consistency scores
        metrics.class_consistency = self._calculate_element_consistency(
            set(metrics.classes_found), set(metrics.classes_documented)
        )
        
        metrics.method_consistency = self._calculate_element_consistency(
            set(metrics.methods_found), set(metrics.methods_documented)
        )
        
        metrics.function_consistency = self._calculate_element_consistency(
            set(metrics.functions_found), set(metrics.functions_documented)
        )
        
        metrics.api_consistency = self._calculate_element_consistency(
            set(metrics.api_endpoints_found), set(metrics.api_endpoints_documented)
        )
        
        # Calculate overall consistency score
        if metrics.total_code_elements > 0:
            # Count how many code elements are documented
            documented_code_elements = 0
            
            for found_element in metrics.classes_found:
                if found_element in metrics.classes_documented:
                    documented_code_elements += 1
                    
            for found_element in metrics.methods_found:
                if found_element in metrics.methods_documented:
                    documented_code_elements += 1
                    
            for found_element in metrics.functions_found:
                if found_element in metrics.functions_documented:
                    documented_code_elements += 1
                    
            for found_element in metrics.api_endpoints_found:
                if found_element in metrics.api_endpoints_documented:
                    documented_code_elements += 1
            
            metrics.consistency_score = (documented_code_elements / metrics.total_code_elements) * 100
            metrics.coverage_ratio = documented_code_elements / metrics.total_code_elements
        else:
            # If no code elements found, score based on documentation presence
            metrics.consistency_score = 50.0 if metrics.documented_elements > 0 else 0.0
            metrics.coverage_ratio = 0.0
    
    def _calculate_element_consistency(self, found_elements: Set[str], documented_elements: Set[str]) -> float:
        """Calculate consistency score for a specific element type."""
        if not found_elements:
            # No elements found in code, so score based on documentation presence
            return 50.0 if documented_elements else 100.0
        
        # Calculate how many found elements are documented
        intersection = found_elements.intersection(documented_elements)
        consistency = (len(intersection) / len(found_elements)) * 100
        
        # Bonus points for comprehensive documentation (more documented than found)
        if len(documented_elements) > len(found_elements):
            bonus = min(10, (len(documented_elements) - len(found_elements)) * 2)
            consistency = min(100, consistency + bonus)
        
        return consistency