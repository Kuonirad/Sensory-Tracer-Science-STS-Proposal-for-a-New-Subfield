"""
Configuration Management for README Quality Platform

Provides centralized configuration management with support for environment
variables, config files, and runtime customization of analysis parameters.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
from dataclasses import dataclass, field


@dataclass
class AnalysisConfig:
    """Configuration for analysis behavior and scoring."""
    
    # Scoring weights for different dimensions (must sum to 1.0)
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        'readability': 0.25,
        'structural': 0.30,
        'complexity': 0.20,
        'consistency': 0.25,
    })
    
    # Quality thresholds for grade assignments
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'excellent': 90.0,
        'good': 75.0,
        'fair': 60.0,
        'poor': 45.0,
    })
    
    # Readability configuration
    readability_config: Dict[str, Any] = field(default_factory=lambda: {
        'target_grade_level': 12.0,  # Optimal grade level for technical docs
        'max_acceptable_grade': 16.0,  # Maximum before penalty
        'preferred_consensus': ['easy', 'fairly easy', 'standard'],
    })
    
    # Structural requirements
    structural_config: Dict[str, Any] = field(default_factory=lambda: {
        'essential_sections': [
            'title', 'description', 'installation', 'usage', 'examples'
        ],
        'bonus_sections': [
            'api_docs', 'contributing', 'license', 'changelog', 'badges', 'toc'
        ],
        'min_section_count': 3,
        'max_recommended_sections': 15,
    })
    
    # Complexity preferences
    complexity_config: Dict[str, Any] = field(default_factory=lambda: {
        'preferred_sophistication': 'intermediate',
        'min_code_blocks': 1,
        'min_links': 3,
        'encourage_images': True,
        'encourage_tables': True,
    })
    
    # Consistency analysis settings
    consistency_config: Dict[str, Any] = field(default_factory=lambda: {
        'min_coverage_ratio': 0.3,  # 30% of code elements should be documented
        'target_coverage_ratio': 0.7,  # 70% for excellent score
        'analyze_repository': True,
        'file_extensions': [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', 
            '.rs', '.cs', '.rb', '.php', '.cpp', '.c', '.h'
        ],
        'exclude_directories': [
            'node_modules', '.git', '__pycache__', 'venv', 'env',
            'build', 'dist', 'target', '.idea', '.vscode'
        ],
    })
    
    # Output formatting preferences
    output_config: Dict[str, Any] = field(default_factory=lambda: {
        'include_debug_info': False,
        'detailed_recommendations': True,
        'include_element_breakdown': False,
        'max_recommendations': 10,
    })


@dataclass
class ServerConfig:
    """Configuration for web server and API."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_enabled: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])
    
    # API rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per minute
    
    # GitHub integration
    github_token: Optional[str] = None
    github_cache_ttl: int = 300  # 5 minutes
    
    # File upload limits
    max_file_size_mb: int = 10
    max_request_size_mb: int = 50


@dataclass
class DatabaseConfig:
    """Configuration for result storage and caching."""
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_max_size: int = 1000  # Maximum cached results
    
    # Storage settings
    storage_type: str = "file"  # "file", "sqlite", "postgresql"
    storage_path: str = "./results"
    
    # Database connection (if using database storage)
    db_url: Optional[str] = None
    db_pool_size: int = 5


class Config:
    """
    Main configuration class that manages all platform settings.
    
    Supports loading from:
    - Environment variables
    - YAML/JSON configuration files
    - Runtime customization
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.analysis = AnalysisConfig()
        self.server = ServerConfig()
        self.database = DatabaseConfig()
        
        # Load from file if provided
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
        
        # Override with environment variables
        self.load_from_env()
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from YAML or JSON file."""
        config_path = Path(config_file)
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            # Update configuration sections
            self._update_from_dict(config_data)
            
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        
        # Server configuration
        self.server.host = os.getenv('README_SERVER_HOST', self.server.host)
        self.server.port = int(os.getenv('README_SERVER_PORT', self.server.port))
        self.server.debug = os.getenv('README_DEBUG', '').lower() in ['true', '1', 'yes']
        
        # GitHub integration
        self.server.github_token = os.getenv('GITHUB_TOKEN', self.server.github_token)
        
        # Database configuration
        self.database.db_url = os.getenv('DATABASE_URL', self.database.db_url)
        self.database.storage_path = os.getenv('README_STORAGE_PATH', self.database.storage_path)
        
        # Analysis weights from environment
        readability_weight = os.getenv('README_READABILITY_WEIGHT')
        if readability_weight:
            self.analysis.scoring_weights['readability'] = float(readability_weight)
        
        structural_weight = os.getenv('README_STRUCTURAL_WEIGHT')  
        if structural_weight:
            self.analysis.scoring_weights['structural'] = float(structural_weight)
        
        complexity_weight = os.getenv('README_COMPLEXITY_WEIGHT')
        if complexity_weight:
            self.analysis.scoring_weights['complexity'] = float(complexity_weight)
        
        consistency_weight = os.getenv('README_CONSISTENCY_WEIGHT')
        if consistency_weight:
            self.analysis.scoring_weights['consistency'] = float(consistency_weight)
        
        # Normalize weights to sum to 1.0
        self._normalize_weights()
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        
        # Update analysis config
        if 'analysis' in config_data:
            analysis_data = config_data['analysis']
            
            if 'scoring_weights' in analysis_data:
                self.analysis.scoring_weights.update(analysis_data['scoring_weights'])
                self._normalize_weights()
            
            if 'quality_thresholds' in analysis_data:
                self.analysis.quality_thresholds.update(analysis_data['quality_thresholds'])
            
            for config_key in ['readability_config', 'structural_config', 
                              'complexity_config', 'consistency_config', 'output_config']:
                if config_key in analysis_data:
                    current_config = getattr(self.analysis, config_key)
                    current_config.update(analysis_data[config_key])
        
        # Update server config
        if 'server' in config_data:
            server_data = config_data['server']
            for key, value in server_data.items():
                if hasattr(self.server, key):
                    setattr(self.server, key, value)
        
        # Update database config
        if 'database' in config_data:
            database_data = config_data['database']
            for key, value in database_data.items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
    
    def _normalize_weights(self) -> None:
        """Normalize scoring weights to sum to 1.0."""
        total_weight = sum(self.analysis.scoring_weights.values())
        if total_weight > 0:
            for key in self.analysis.scoring_weights:
                self.analysis.scoring_weights[key] /= total_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'analysis': {
                'scoring_weights': self.analysis.scoring_weights,
                'quality_thresholds': self.analysis.quality_thresholds,
                'readability_config': self.analysis.readability_config,
                'structural_config': self.analysis.structural_config,
                'complexity_config': self.analysis.complexity_config,
                'consistency_config': self.analysis.consistency_config,
                'output_config': self.analysis.output_config,
            },
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'debug': self.server.debug,
                'cors_enabled': self.server.cors_enabled,
                'cors_origins': self.server.cors_origins,
                'rate_limit_enabled': self.server.rate_limit_enabled,
                'rate_limit_requests': self.server.rate_limit_requests,
                'github_cache_ttl': self.server.github_cache_ttl,
                'max_file_size_mb': self.server.max_file_size_mb,
                'max_request_size_mb': self.server.max_request_size_mb,
            },
            'database': {
                'cache_enabled': self.database.cache_enabled,
                'cache_ttl_seconds': self.database.cache_ttl_seconds,
                'cache_max_size': self.database.cache_max_size,
                'storage_type': self.database.storage_type,
                'storage_path': self.database.storage_path,
                'db_pool_size': self.database.db_pool_size,
            }
        }
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to file."""
        config_path = Path(config_file)
        config_data = self.to_dict()
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif config_path.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    def get_analyzer_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for the analyzer."""
        return {
            'scoring_weights': self.analysis.scoring_weights,
            'thresholds': self.analysis.quality_thresholds,
            'readability': self.analysis.readability_config,
            'structural': self.analysis.structural_config,
            'complexity': self.analysis.complexity_config,
            'consistency': self.analysis.consistency_config,
            'output': self.analysis.output_config,
        }
    
    def create_custom_weights(self, 
                             readability: float = None,
                             structural: float = None,
                             complexity: float = None,
                             consistency: float = None) -> Dict[str, float]:
        """
        Create custom scoring weights configuration.
        
        Args:
            readability: Weight for readability dimension (0.0-1.0)
            structural: Weight for structural dimension (0.0-1.0)
            complexity: Weight for complexity dimension (0.0-1.0)
            consistency: Weight for consistency dimension (0.0-1.0)
            
        Returns:
            Normalized weights dictionary
        """
        weights = {}
        
        if readability is not None:
            weights['readability'] = readability
        if structural is not None:
            weights['structural'] = structural
        if complexity is not None:
            weights['complexity'] = complexity
        if consistency is not None:
            weights['consistency'] = consistency
        
        # Fill in missing weights with defaults
        default_weights = self.analysis.scoring_weights
        for key in default_weights:
            if key not in weights:
                weights[key] = default_weights[key]
        
        # Normalize to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def set_config(config: Config) -> None:
    """Set global configuration instance."""
    global _config_instance
    _config_instance = config


def load_config(config_file: str) -> Config:
    """Load configuration from file and set as global instance."""
    config = Config(config_file)
    set_config(config)
    return config