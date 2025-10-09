"""
FastAPI REST API Server for README Quality Platform

Comprehensive API providing all analysis capabilities through RESTful endpoints
with support for file uploads, GitHub integration, batch processing, and real-time analysis.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, Field

from ..core import ReadmeAnalyzer, Config, get_config
from ..analyzers import GitHubAnalyzer


# Pydantic models for request/response
class AnalyzeContentRequest(BaseModel):
    """Request model for analyzing README content."""
    content: str = Field(..., description="README content to analyze")
    repository_url: Optional[HttpUrl] = Field(None, description="Repository URL for context")
    include_code_analysis: bool = Field(False, description="Include code consistency analysis")


class AnalyzeRepositoryRequest(BaseModel):
    """Request model for analyzing GitHub repository."""
    repository_url: HttpUrl = Field(..., description="GitHub repository URL")
    include_code_analysis: bool = Field(True, description="Include code consistency analysis")
    branch: str = Field("main", description="Branch to analyze")


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch analysis."""
    targets: List[str] = Field(..., description="List of README files or repository URLs")
    include_code_analysis: bool = Field(True, description="Include code consistency analysis")


class CustomWeightsRequest(BaseModel):
    """Request model for custom scoring weights."""
    readability: float = Field(0.25, ge=0, le=1, description="Readability weight")
    structural: float = Field(0.30, ge=0, le=1, description="Structural weight") 
    complexity: float = Field(0.20, ge=0, le=1, description="Complexity weight")
    consistency: float = Field(0.25, ge=0, le=1, description="Consistency weight")


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis results."""
    success: bool
    results: List[Dict[str, Any]] = []
    summary: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    total_processed: int = 0


# Initialize FastAPI app
app = FastAPI(
    title="README Quality Platform API",
    description="Comprehensive README quality assessment with multi-dimensional analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get analyzer instance
def get_analyzer(config: Config = Depends(get_config)) -> ReadmeAnalyzer:
    """Get ReadmeAnalyzer instance with current configuration."""
    return ReadmeAnalyzer(config.get_analyzer_config())


def get_github_analyzer(config: Config = Depends(get_config)) -> GitHubAnalyzer:
    """Get GitHubAnalyzer instance with current configuration."""
    return GitHubAnalyzer(config.server.github_token)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    return """
    <html>
        <head>
            <title>README Quality Platform API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
                .endpoint { background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { color: #059669; font-weight: bold; }
                code { background: #e5e7eb; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1 class="header">README Quality Platform API</h1>
            <p>Comprehensive README quality assessment with multi-dimensional analysis</p>
            
            <h2>Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/analyze/content</code>
                <p>Analyze README content directly</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/analyze/file</code>
                <p>Upload and analyze README file</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/analyze/repository</code>
                <p>Analyze README from GitHub repository</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/analyze/batch</code>
                <p>Batch analysis of multiple targets</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/health</code>
                <p>Health check endpoint</p>
            </div>
            
            <h2>Documentation</h2>
            <p><a href="/docs">Interactive API Documentation (Swagger)</a></p>
            <p><a href="/redoc">Alternative Documentation (ReDoc)</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "README Quality Platform API",
        "version": "1.0.0"
    }


@app.post("/analyze/content", response_model=AnalysisResponse)
async def analyze_content(
    request: AnalyzeContentRequest,
    analyzer: ReadmeAnalyzer = Depends(get_analyzer)
):
    """
    Analyze README content directly.
    
    Performs comprehensive quality analysis on provided README content
    across readability, structural, complexity, and consistency dimensions.
    """
    
    try:
        # Perform analysis
        analysis = analyzer.analyze_content(
            content=request.content,
            repository_url=str(request.repository_url) if request.repository_url else None
        )
        
        return AnalysisResponse(
            success=True,
            analysis=analysis.to_dict(),
            processing_time_ms=analysis.analysis_duration_ms
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/analyze/file", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(..., description="README file to analyze"),
    include_code_analysis: bool = False,
    analyzer: ReadmeAnalyzer = Depends(get_analyzer)
):
    """
    Upload and analyze README file.
    
    Accepts file upload and performs comprehensive quality analysis.
    Optionally includes code consistency analysis if repository context provided.
    """
    
    try:
        # Validate file
        if not file.filename.lower().startswith('readme'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a README file"
            )
        
        # Read file content
        content = await file.read()
        
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content_str = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Could not decode file content. Please ensure UTF-8 encoding."
                )
        
        # Perform analysis
        analysis = analyzer.analyze_content(
            content=content_str,
            readme_path=file.filename
        )
        
        return AnalysisResponse(
            success=True,
            analysis=analysis.to_dict(),
            processing_time_ms=analysis.analysis_duration_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/analyze/repository", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
    github_analyzer: GitHubAnalyzer = Depends(get_github_analyzer)
):
    """
    Analyze README from GitHub repository.
    
    Fetches README from specified GitHub repository and performs
    comprehensive analysis with optional code consistency checking.
    """
    
    try:
        # Perform GitHub analysis
        analysis = github_analyzer.analyze_repository(
            repo_url=str(request.repository_url),
            include_code_analysis=request.include_code_analysis,
            branch=request.branch
        )
        
        return AnalysisResponse(
            success=True,
            analysis=analysis.to_dict(),
            processing_time_ms=analysis.analysis_duration_ms
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def batch_analyze(
    request: BatchAnalyzeRequest,
    background_tasks: BackgroundTasks,
    analyzer: ReadmeAnalyzer = Depends(get_analyzer),
    github_analyzer: GitHubAnalyzer = Depends(get_github_analyzer)
):
    """
    Perform batch analysis of multiple targets.
    
    Analyzes multiple README files or repositories in a single request.
    Returns individual results plus aggregate summary statistics.
    """
    
    try:
        results = []
        errors = []
        
        for target in request.targets:
            try:
                if target.startswith(('http://', 'https://')):
                    # GitHub repository
                    analysis = github_analyzer.analyze_repository(
                        repo_url=target,
                        include_code_analysis=request.include_code_analysis
                    )
                else:
                    # Local file (in real deployment, this would need file handling)
                    raise HTTPException(
                        status_code=400,
                        detail="Local file analysis not supported in batch mode via API"
                    )
                
                results.append({
                    'target': target,
                    'analysis': analysis.to_dict(),
                    'success': True
                })
                
            except Exception as e:
                errors.append(f"Failed to analyze {target}: {str(e)}")
                results.append({
                    'target': target,
                    'error': str(e),
                    'success': False
                })
        
        # Generate summary
        successful_results = [r for r in results if r.get('success')]
        summary = generate_batch_summary(successful_results) if successful_results else None
        
        return BatchAnalysisResponse(
            success=True,
            results=results,
            summary=summary,
            errors=errors,
            total_processed=len(request.targets)
        )
        
    except Exception as e:
        return BatchAnalysisResponse(
            success=False,
            errors=[str(e)],
            total_processed=0
        )


@app.post("/analyze/custom-weights", response_model=AnalysisResponse)
async def analyze_with_custom_weights(
    content_request: AnalyzeContentRequest,
    weights: CustomWeightsRequest,
    config: Config = Depends(get_config)
):
    """
    Analyze content with custom scoring weights.
    
    Allows customization of the relative importance of different
    analysis dimensions (readability, structural, complexity, consistency).
    """
    
    try:
        # Validate weights sum to 1.0
        total_weight = weights.readability + weights.structural + weights.complexity + weights.consistency
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 1.0, got {total_weight}"
            )
        
        # Create custom config
        custom_config = config.get_analyzer_config()
        custom_config['scoring_weights'] = {
            'readability': weights.readability,
            'structural': weights.structural,
            'complexity': weights.complexity,
            'consistency': weights.consistency,
        }
        
        # Create analyzer with custom weights
        analyzer = ReadmeAnalyzer(custom_config)
        
        # Perform analysis
        analysis = analyzer.analyze_content(
            content=content_request.content,
            repository_url=str(content_request.repository_url) if content_request.repository_url else None
        )
        
        return AnalysisResponse(
            success=True,
            analysis=analysis.to_dict(),
            processing_time_ms=analysis.analysis_duration_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@app.get("/config")
async def get_configuration(config: Config = Depends(get_config)):
    """Get current platform configuration."""
    return config.to_dict()


@app.get("/github/rate-limit")
async def get_github_rate_limit(github_analyzer: GitHubAnalyzer = Depends(get_github_analyzer)):
    """Get GitHub API rate limit status."""
    return github_analyzer.get_rate_limit_status()


@app.get("/github/search")
async def search_repositories(
    topic: str,
    limit: int = 10,
    min_stars: int = 0,
    github_analyzer: GitHubAnalyzer = Depends(get_github_analyzer)
):
    """
    Search GitHub repositories by topic.
    
    Useful for finding repositories to analyze or benchmarking
    README quality across projects in specific domains.
    """
    
    try:
        results = github_analyzer.search_repositories_by_topic(
            topic=topic,
            limit=limit,
            min_stars=min_stars
        )
        
        return {
            "success": True,
            "repositories": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repositories": [],
            "count": 0
        }


def generate_batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for batch analysis results."""
    
    if not results:
        return {}
    
    # Extract scores
    overall_scores = []
    dimension_scores = {
        'readability': [],
        'structural': [],
        'complexity': [],
        'consistency': []
    }
    
    for result in results:
        if result.get('success') and 'analysis' in result:
            analysis = result['analysis']
            quality = analysis.get('quality', {})
            
            overall_scores.append(quality.get('overall_score', 0))
            
            for dim in dimension_scores:
                score_key = f'{dim}_score'
                if score_key in quality:
                    dimension_scores[dim].append(quality[score_key])
    
    # Calculate statistics
    def calc_stats(scores):
        if not scores:
            return {}
        return {
            'mean': sum(scores) / len(scores),
            'min': min(scores),
            'max': max(scores),
            'count': len(scores)
        }
    
    summary = {
        'total_analyzed': len(results),
        'successful_analyses': len([r for r in results if r.get('success')]),
        'overall_scores': calc_stats(overall_scores),
        'dimension_scores': {
            dim: calc_stats(scores) for dim, scores in dimension_scores.items()
        }
    }
    
    return summary


def main():
    """Main entry point for running the API server."""
    config = get_config()
    
    uvicorn.run(
        "readme_quality_platform.api.server:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug,
        access_log=True
    )


if __name__ == "__main__":
    main()