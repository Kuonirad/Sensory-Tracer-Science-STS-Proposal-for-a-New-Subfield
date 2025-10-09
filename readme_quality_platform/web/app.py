"""
Web Dashboard Application for README Quality Platform

Interactive dashboard providing visual analysis interface, real-time results,
comprehensive reporting, and user-friendly access to all platform features.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import tempfile
from datetime import datetime
import logging

# Configure basic logging if not already configured elsewhere
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import plotly.graph_objs as go
import plotly.utils
import uvicorn

from ..core import ReadmeAnalyzer, Config, get_config
from ..analyzers import GitHubAnalyzer


# Initialize FastAPI app for web dashboard
app = FastAPI(
    title="README Quality Dashboard",
    description="Interactive web dashboard for comprehensive README quality assessment"
)

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Create static files directory if it doesn't exist
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# CORS for API endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "README Quality Dashboard"
    })


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    """Analysis page with input forms."""
    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "title": "Analyze README"
    })


@app.get("/batch", response_class=HTMLResponse)
async def batch_page(request: Request):
    """Batch analysis page."""
    return templates.TemplateResponse("batch.html", {
        "request": request,
        "title": "Batch Analysis"
    })


@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    """Comparison page."""
    return templates.TemplateResponse("compare.html", {
        "request": request,
        "title": "Compare README Files"
    })


@app.post("/api/analyze/content")
async def api_analyze_content(
    content: str = Form(...),
    repository_url: Optional[str] = Form(None),
    custom_weights: Optional[str] = Form(None)
):
    """API endpoint for analyzing README content."""
    
    try:
        config = get_config()
        
        # Parse custom weights if provided
        if custom_weights:
            weights = json.loads(custom_weights)
            analyzer_config = config.get_analyzer_config()
            analyzer_config['scoring_weights'] = weights
            analyzer = ReadmeAnalyzer(analyzer_config)
        else:
            analyzer = ReadmeAnalyzer(config.get_analyzer_config())
        
        # Perform analysis
        analysis = analyzer.analyze_content(
            content=content,
            repository_url=repository_url
        )
        
        # Generate visualizations
        charts = generate_analysis_charts(analysis)
        
        return {
            "success": True,
            "analysis": analysis.to_dict(),
            "charts": charts,
            "summary": analyzer.get_analysis_summary(analysis)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/analyze/file")
async def api_analyze_file(
    file: UploadFile = File(...),
    repository_url: Optional[str] = Form(None),
    custom_weights: Optional[str] = Form(None)
):
    """API endpoint for analyzing uploaded README file."""
    
    try:
        # Read file content
        content = await file.read()
        
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1', errors='ignore')
        
        config = get_config()
        
        # Parse custom weights if provided
        if custom_weights:
            weights = json.loads(custom_weights)
            analyzer_config = config.get_analyzer_config()
            analyzer_config['scoring_weights'] = weights
            analyzer = ReadmeAnalyzer(analyzer_config)
        else:
            analyzer = ReadmeAnalyzer(config.get_analyzer_config())
        
        # Perform analysis
        analysis = analyzer.analyze_content(
            content=content_str,
            readme_path=file.filename,
            repository_url=repository_url
        )
        
        # Generate visualizations
        charts = generate_analysis_charts(analysis)
        
        return {
            "success": True,
            "analysis": analysis.to_dict(),
            "charts": charts,
            "summary": analyzer.get_analysis_summary(analysis),
            "filename": file.filename
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/analyze/repository")
async def api_analyze_repository(
    repository_url: str = Form(...),
    branch: str = Form("main"),
    include_code: bool = Form(True),
    custom_weights: Optional[str] = Form(None)
):
    """API endpoint for analyzing GitHub repository."""
    
    try:
        config = get_config()
        github_analyzer = GitHubAnalyzer(config.server.github_token)
        
        # Perform analysis
        analysis = github_analyzer.analyze_repository(
            repo_url=repository_url,
            include_code_analysis=include_code,
            branch=branch
        )
        
        # Generate visualizations
        charts = generate_analysis_charts(analysis)
        
        # Create analyzer for summary (with custom weights if provided)
        if custom_weights:
            weights = json.loads(custom_weights)
            analyzer_config = config.get_analyzer_config()
            analyzer_config['scoring_weights'] = weights
            analyzer = ReadmeAnalyzer(analyzer_config)
        else:
            analyzer = ReadmeAnalyzer(config.get_analyzer_config())
        
        return {
            "success": True,
            "analysis": analysis.to_dict(),
            "charts": charts,
            "summary": analyzer.get_analysis_summary(analysis),
            "repository_url": repository_url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/batch/analyze")
async def api_batch_analyze(
    targets: str = Form(...),  # JSON string of target list
    include_code: bool = Form(True),
    custom_weights: Optional[str] = Form(None)
):
    """API endpoint for batch analysis."""
    
    try:
        targets_list = json.loads(targets)
        config = get_config()
        
        # Setup analyzers
        if custom_weights:
            weights = json.loads(custom_weights)
            analyzer_config = config.get_analyzer_config()
            analyzer_config['scoring_weights'] = weights
            analyzer = ReadmeAnalyzer(analyzer_config)
        else:
            analyzer = ReadmeAnalyzer(config.get_analyzer_config())
        
        github_analyzer = GitHubAnalyzer(config.server.github_token)
        
        # Process targets
        results = []
        for target in targets_list:
            try:
                if target.startswith(('http://', 'https://')):
                    # GitHub repository
                    analysis = github_analyzer.analyze_repository(
                        repo_url=target,
                        include_code_analysis=include_code
                    )
                else:
                    # Skip local files for web interface
                    results.append({
                        "target": target,
                        "success": False,
                        "error": "Local file analysis not supported in web interface"
                    })
                    continue
                
                results.append({
                    "target": target,
                    "success": True,
                    "analysis": analysis.to_dict(),
                    "summary": analyzer.get_analysis_summary(analysis)
                })
                
                logging.exception(f"Error analyzing target '{target}' in batch analysis")
            except Exception as e:
                results.append({
                    "target": target,
                    "success": False,
                    "error": "An internal error occurred during analysis"
                })
        
        # Generate batch summary
        successful_results = [r for r in results if r.get('success')]
        batch_summary = generate_batch_summary(successful_results)
        
        # Generate batch visualization
        batch_chart = generate_batch_chart(successful_results)
        
        return {
            "success": True,
            "results": results,
            "summary": batch_summary,
            "chart": batch_chart,
        logging.exception("Unhandled exception in batch analyze API endpoint")
            "total_processed": len(targets_list)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": "An internal error occurred during batch analysis"
        }


def generate_analysis_charts(analysis) -> Dict[str, str]:
    """Generate Plotly charts for analysis results."""
    
    charts = {}
    
    # Dimension scores radar chart
    dimensions = ['Readability', 'Structure', 'Complexity', 'Consistency']
    scores = [
        analysis.quality.readability_score,
        analysis.quality.structural_score,
        analysis.quality.complexity_score,
        analysis.quality.consistency_score
    ]
    
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=dimensions,
        fill='toself',
        name='Scores',
        line_color='rgb(59, 130, 246)'
    ))
    
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Quality Dimensions",
        font=dict(size=12)
    )
    
    charts['radar'] = json.dumps(radar_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Score distribution bar chart
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=dimensions,
        y=scores,
        marker_color=['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b'],
        text=[f'{score:.1f}' for score in scores],
        textposition='auto'
    ))
    
    bar_fig.update_layout(
        title="Dimension Scores",
        xaxis_title="Dimensions",
        yaxis_title="Score (0-100)",
        yaxis=dict(range=[0, 100]),
        font=dict(size=12)
    )
    
    charts['bar'] = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Readability metrics gauge
    if analysis.readability.flesch_reading_ease > 0:
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=analysis.readability.flesch_reading_ease,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Flesch Reading Ease"},
            delta={'reference': 60},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 30], 'color': "lightgray"},
                       {'range': [30, 50], 'color': "yellow"},
                       {'range': [50, 70], 'color': "orange"},
                       {'range': [70, 100], 'color': "lightgreen"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 90}}))
        
        gauge_fig.update_layout(font=dict(size=12))
        charts['gauge'] = json.dumps(gauge_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return charts


def generate_batch_summary(results) -> Dict[str, Any]:
    """Generate summary statistics for batch results."""
    
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
        analysis = result['analysis']
        quality = analysis['quality']
        
        overall_scores.append(quality['overall_score'])
        dimension_scores['readability'].append(quality['readability_score'])
        dimension_scores['structural'].append(quality['structural_score'])
        dimension_scores['complexity'].append(quality['complexity_score'])
        dimension_scores['consistency'].append(quality['consistency_score'])
    
    # Calculate statistics
    def calc_stats(scores):
        return {
            'mean': sum(scores) / len(scores),
            'min': min(scores),
            'max': max(scores),
            'count': len(scores)
        }
    
    return {
        'total_analyzed': len(results),
        'overall_stats': calc_stats(overall_scores),
        'dimension_stats': {dim: calc_stats(scores) for dim, scores in dimension_scores.items()}
    }


def generate_batch_chart(results) -> str:
    """Generate chart for batch analysis results."""
    
    if not results:
        return ""
    
    # Extract data
    targets = [result['target'][:30] + '...' if len(result['target']) > 30 else result['target'] 
               for result in results]
    overall_scores = [result['analysis']['quality']['overall_score'] for result in results]
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=targets,
        y=overall_scores,
        marker_color=['#10b981' if score >= 75 else '#f59e0b' if score >= 50 else '#ef4444' 
                     for score in overall_scores],
        text=[f'{score:.1f}' for score in overall_scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Batch Analysis Results",
        xaxis_title="Targets",
        yaxis_title="Overall Score",
        yaxis=dict(range=[0, 100]),
        xaxis_tickangle=-45,
        font=dict(size=10)
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.get("/results/{result_id}")
async def get_result(request: Request, result_id: str):
    """Display detailed results page."""
    # In a real implementation, this would retrieve stored results
    return templates.TemplateResponse("results.html", {
        "request": request,
        "title": "Analysis Results",
        "result_id": result_id
    })


def main():
    """Main entry point for running the web dashboard."""
    config = get_config()
    
    # Create templates if they don't exist
    create_default_templates()
    
    uvicorn.run(
        "readme_quality_platform.web.app:app",
        host=config.server.host,
        port=config.server.port + 1,  # Use different port than API
        reload=config.server.debug,
        access_log=True
    )


def create_default_templates():
    """Create default HTML templates if they don't exist."""
    
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Create basic dashboard template
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8 text-blue-600">README Quality Platform</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Analyze Single README</h2>
                <p class="text-gray-600 mb-4">Upload a file or paste content for comprehensive quality analysis.</p>
                <a href="/analyze" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">Analyze Now</a>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Batch Analysis</h2>
                <p class="text-gray-600 mb-4">Analyze multiple repositories or files simultaneously.</p>
                <a href="/batch" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">Batch Analyze</a>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Compare READMEs</h2>
                <p class="text-gray-600 mb-4">Compare quality metrics across multiple README files.</p>
                <a href="/compare" class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded">Compare</a>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4">Features</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h3 class="font-medium">Multi-Dimensional Analysis</h3>
                    <p class="text-gray-600 text-sm">Readability, Structure, Complexity, and Code Consistency</p>
                </div>
                <div>
                    <h3 class="font-medium">GitHub Integration</h3>
                    <p class="text-gray-600 text-sm">Direct analysis from GitHub repositories</p>
                </div>
                <div>
                    <h3 class="font-medium">Actionable Recommendations</h3>
                    <p class="text-gray-600 text-sm">Specific suggestions for improvement</p>
                </div>
                <div>
                    <h3 class="font-medium">Visual Reports</h3>
                    <p class="text-gray-600 text-sm">Interactive charts and comprehensive metrics</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    (templates_dir / "dashboard.html").write_text(dashboard_html)
    
    # Create other template placeholders...
    # (Additional templates would be created here for analyze.html, batch.html, etc.)


if __name__ == "__main__":
    main()