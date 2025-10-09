"""
GitHub Integration for README Quality Analysis

Provides seamless integration with GitHub repositories for analyzing README files
directly from GitHub, with support for repository metadata and code consistency analysis.
"""

import os
import re
import tempfile
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
from github import Github
from github.GithubException import GithubException

from ..core import ReadmeAnalyzer, ReadmeAnalysis


class GitHubAnalyzer:
    """
    GitHub-specific README analyzer with repository integration.
    
    Provides direct analysis of README files from GitHub repositories with
    optional code consistency analysis using the GitHub API and git cloning.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub analyzer.
        
        Args:
            github_token: Optional GitHub token for authenticated API access
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.github_client = None
        
        if self.github_token:
            try:
                self.github_client = Github(self.github_token)
                # Test the token
                self.github_client.get_user().login
            except Exception as e:
                print(f"Warning: GitHub token invalid or expired: {e}")
                self.github_client = None
        
        # Initialize core analyzer
        self.analyzer = ReadmeAnalyzer()
    
    def analyze_repository(self, 
                          repo_url: str, 
                          include_code_analysis: bool = True,
                          branch: str = "main") -> ReadmeAnalysis:
        """
        Analyze README from GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            include_code_analysis: Whether to include code consistency analysis
            branch: Branch to analyze (default: main)
            
        Returns:
            ReadmeAnalysis: Complete analysis results
        """
        
        # Parse repository info from URL
        repo_info = self._parse_repo_url(repo_url)
        if not repo_info:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        owner, repo_name = repo_info
        
        try:
            # Get README content via API
            readme_content, readme_path = self._get_readme_content(owner, repo_name, branch)
            
            if not readme_content:
                raise ValueError(f"No README file found in repository {owner}/{repo_name}")
            
            # Get repository metadata
            repo_metadata = self._get_repo_metadata(owner, repo_name)
            
            # Perform analysis
            if include_code_analysis:
                # Clone repository for code analysis
                with tempfile.TemporaryDirectory() as temp_dir:
                    repo_path = self._clone_repository(repo_url, temp_dir, branch)
                    
                    analysis = self.analyzer.analyze_content(
                        content=readme_content,
                        readme_path=readme_path,
                        repository_path=repo_path,
                        repository_url=repo_url
                    )
            else:
                # Analyze README only
                analysis = self.analyzer.analyze_content(
                    content=readme_content,
                    readme_path=readme_path,
                    repository_url=repo_url
                )
            
            # Add GitHub-specific metadata
            self._add_github_metadata(analysis, repo_metadata)
            
            return analysis
            
        except Exception as e:
            # Return analysis with error
            analysis = ReadmeAnalysis(
                repository_url=repo_url,
                readme_path="README.md",
                error_messages=[f"GitHub analysis failed: {str(e)}"]
            )
            return analysis
    
    def analyze_readme_url(self, readme_url: str) -> ReadmeAnalysis:
        """
        Analyze README from direct GitHub file URL.
        
        Args:
            readme_url: Direct URL to README file on GitHub
            
        Returns:
            ReadmeAnalysis: Analysis results
        """
        
        try:
            # Download README content
            response = requests.get(readme_url, timeout=30)
            response.raise_for_status()
            
            readme_content = response.text
            
            # Analyze content
            analysis = self.analyzer.analyze_content(
                content=readme_content,
                readme_path=readme_url,
                repository_url=self._extract_repo_url_from_file_url(readme_url)
            )
            
            return analysis
            
        except Exception as e:
            analysis = ReadmeAnalysis(
                readme_path=readme_url,
                error_messages=[f"Failed to analyze README URL: {str(e)}"]
            )
            return analysis
    
    def batch_analyze_repositories(self, 
                                  repo_urls: List[str],
                                  include_code_analysis: bool = True) -> List[ReadmeAnalysis]:
        """
        Analyze multiple repositories in batch.
        
        Args:
            repo_urls: List of GitHub repository URLs
            include_code_analysis: Whether to include code consistency analysis
            
        Returns:
            List of ReadmeAnalysis results
        """
        
        results = []
        
        for repo_url in repo_urls:
            try:
                analysis = self.analyze_repository(repo_url, include_code_analysis)
                results.append(analysis)
            except Exception as e:
                # Create error result
                error_analysis = ReadmeAnalysis(
                    repository_url=repo_url,
                    error_messages=[f"Batch analysis failed: {str(e)}"]
                )
                results.append(error_analysis)
        
        return results
    
    def search_repositories_by_topic(self, 
                                   topic: str,
                                   limit: int = 10,
                                   min_stars: int = 0) -> List[Dict[str, Any]]:
        """
        Search GitHub repositories by topic for README analysis.
        
        Args:
            topic: GitHub topic to search for
            limit: Maximum number of repositories to return
            min_stars: Minimum star count filter
            
        Returns:
            List of repository information dictionaries
        """
        
        if not self.github_client:
            raise ValueError("GitHub token required for repository search")
        
        try:
            # Search repositories
            query = f"topic:{topic}"
            if min_stars > 0:
                query += f" stars:>={min_stars}"
            
            repositories = self.github_client.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )
            
            results = []
            count = 0
            
            for repo in repositories:
                if count >= limit:
                    break
                
                repo_info = {
                    'name': repo.full_name,
                    'url': repo.html_url,
                    'clone_url': repo.clone_url,
                    'stars': repo.stargazers_count,
                    'language': repo.language,
                    'description': repo.description,
                    'has_readme': self._repository_has_readme(repo),
                }
                
                results.append(repo_info)
                count += 1
            
            return results
            
        except Exception as e:
            raise ValueError(f"Repository search failed: {str(e)}")
    
    def _parse_repo_url(self, repo_url: str) -> Optional[tuple]:
        """Parse GitHub repository URL to extract owner and repo name."""
        
        # Support various GitHub URL formats
        patterns = [
            r'github\.com[:/]([^/]+)/([^/\.]+)(?:\.git)?/?$',
            r'github\.com/([^/]+)/([^/]+)/?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1), match.group(2)
        
        return None
    
    def _get_readme_content(self, owner: str, repo_name: str, branch: str = "main") -> tuple:
        """Get README content from GitHub repository."""
        
        # Try different README file names
        readme_files = [
            'README.md', 'readme.md', 'README.rst', 'readme.rst',
            'README.txt', 'readme.txt', 'README', 'readme'
        ]
        
        # Try with GitHub API first (if token available)
        if self.github_client:
            try:
                repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                
                for readme_file in readme_files:
                    try:
                        file_content = repo.get_contents(readme_file, ref=branch)
                        if file_content.type == 'file':
                            content = file_content.decoded_content.decode('utf-8')
                            return content, readme_file
                    except GithubException:
                        continue
                        
            except GithubException as e:
                # Fall back to raw content download
                pass
        
        # Try raw content download
        for readme_file in readme_files:
            try:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{readme_file}"
                response = requests.get(raw_url, timeout=30)
                
                if response.status_code == 200:
                    return response.text, readme_file
                    
            except requests.RequestException:
                continue
        
        return None, None
    
    def _get_repo_metadata(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """Get repository metadata from GitHub API."""
        
        metadata = {}
        
        if self.github_client:
            try:
                repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                
                metadata = {
                    'name': repo.full_name,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'issues': repo.open_issues_count,
                    'size': repo.size,
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    'topics': list(repo.get_topics()),
                    'license': repo.license.name if repo.license else None,
                    'has_wiki': repo.has_wiki,
                    'has_pages': repo.has_pages,
                    'default_branch': repo.default_branch,
                }
                
            except GithubException as e:
                metadata['error'] = f"Could not fetch metadata: {str(e)}"
        
        return metadata
    
    def _clone_repository(self, repo_url: str, temp_dir: str, branch: str = "main") -> str:
        """Clone repository to temporary directory for code analysis."""
        
        repo_path = Path(temp_dir) / "repo"
        
        try:
            # Use git command to clone
            clone_url = repo_url
            if not clone_url.endswith('.git'):
                clone_url += '.git'
            
            import subprocess
            
            # Clone with depth 1 for faster cloning
            cmd = [
                'git', 'clone', 
                '--depth', '1',
                '--branch', branch,
                clone_url,
                str(repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                # Try default branch if specified branch fails
                if branch != 'main':
                    cmd[5] = 'main'
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode != 0 and branch != 'master':
                        cmd[5] = 'master'
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")
            
            return str(repo_path)
            
        except Exception as e:
            raise RuntimeError(f"Repository cloning failed: {str(e)}")
    
    def _repository_has_readme(self, repo) -> bool:
        """Check if repository has a README file."""
        
        try:
            readme_files = [
                'README.md', 'readme.md', 'README.rst', 'readme.rst',
                'README.txt', 'readme.txt', 'README', 'readme'
            ]
            
            contents = repo.get_contents("")
            file_names = [item.name for item in contents if item.type == 'file']
            
            return any(readme_file in file_names for readme_file in readme_files)
            
        except Exception:
            return False
    
    def _add_github_metadata(self, analysis: ReadmeAnalysis, metadata: Dict[str, Any]) -> None:
        """Add GitHub-specific metadata to analysis results."""
        
        # Store metadata in analysis (could extend ReadmeAnalysis model for this)
        if hasattr(analysis, 'metadata') or True:  # Add metadata field
            analysis.github_metadata = metadata
    
    def _extract_repo_url_from_file_url(self, file_url: str) -> Optional[str]:
        """Extract repository URL from GitHub file URL."""
        
        # Pattern for GitHub file URLs
        pattern = r'github\.com/([^/]+)/([^/]+)/'
        match = re.search(pattern, file_url)
        
        if match:
            owner, repo = match.groups()
            return f"https://github.com/{owner}/{repo}"
        
        return None
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current GitHub API rate limit status."""
        
        if not self.github_client:
            return {'error': 'No GitHub token configured'}
        
        try:
            rate_limit = self.github_client.get_rate_limit()
            
            return {
                'core': {
                    'limit': rate_limit.core.limit,
                    'remaining': rate_limit.core.remaining,
                    'reset': rate_limit.core.reset.isoformat(),
                },
                'search': {
                    'limit': rate_limit.search.limit,
                    'remaining': rate_limit.search.remaining,
                    'reset': rate_limit.search.reset.isoformat(),
                }
            }
            
        except Exception as e:
            return {'error': f'Could not get rate limit: {str(e)}'}