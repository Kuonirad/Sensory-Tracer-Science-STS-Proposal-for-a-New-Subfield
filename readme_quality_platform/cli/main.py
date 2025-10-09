"""
CLI Interface for README Quality Platform

Comprehensive command-line tool for analyzing README files with rich output,
batch processing, GitHub integration, and various export formats.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.tree import Tree
from rich import print as rprint
import typer

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from readme_quality_platform.core import ReadmeAnalyzer, Config, get_config
from readme_quality_platform.analyzers import GitHubAnalyzer


app = typer.Typer(
    name="readme-analyzer",
    help="Comprehensive README Quality Assessment Platform",
    add_completion=False,
)

console = Console()


@app.command()
def analyze(
    target: str = typer.Argument(
        ..., 
        help="README file path, directory path, or GitHub repository URL"
    ),
    output: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path for results (JSON format)"
    ),
    format: str = typer.Option(
        "rich", 
        "--format", "-f",
        help="Output format: rich, json, table, summary"
    ),
    repository: Optional[str] = typer.Option(
        None,
        "--repository", "-r",
        help="Repository path for consistency analysis"
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config", "-c",
        help="Configuration file path"
    ),
    weights: Optional[str] = typer.Option(
        None,
        "--weights", "-w",
        help="Custom scoring weights as 'r,s,c,n' (readability,structural,complexity,consistency)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed analysis information"
    ),
    include_code: bool = typer.Option(
        True,
        "--include-code/--no-code",
        help="Include code consistency analysis"
    ),
    github_token: Optional[str] = typer.Option(
        None,
        "--github-token",
        help="GitHub token for API access"
    ),
) -> None:
    """
    Analyze README file(s) for quality across multiple dimensions.
    
    Examples:
        readme-analyzer README.md
        readme-analyzer https://github.com/user/repo
        readme-analyzer ./project --repository ./project
        readme-analyzer README.md --format json --output results.json
    """
    
    try:
        # Load configuration
        config = load_configuration(config_file)
        
        # Parse custom weights if provided
        if weights:
            custom_weights = parse_weights(weights)
            config.analysis.scoring_weights = custom_weights
        
        # Set GitHub token if provided
        if github_token:
            config.server.github_token = github_token
        elif not config.server.github_token:
            # Try environment variable
            config.server.github_token = os.getenv('GITHUB_TOKEN')
        
        # Determine analysis type and execute
        if target.startswith(('http://', 'https://')):
            results = analyze_github_repo(target, config, include_code)
        elif os.path.isfile(target):
            results = analyze_single_file(target, repository if include_code else None, config)
        elif os.path.isdir(target):
            results = analyze_directory(target, config, include_code)
        else:
            console.print(f"[red]Error: Target not found: {target}[/red]")
            raise typer.Exit(1)
        
        # Output results
        display_results(results, format, output, verbose)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def batch(
    input_file: str = typer.Argument(
        ...,
        help="File containing list of targets to analyze (one per line)"
    ),
    output_dir: str = typer.Option(
        "./batch_results",
        "--output-dir", "-o",
        help="Directory to save individual analysis results"
    ),
    summary_file: Optional[str] = typer.Option(
        None,
        "--summary", "-s",
        help="Summary report file path"
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config", "-c",
        help="Configuration file path"
    ),
    parallel: int = typer.Option(
        1,
        "--parallel", "-p",
        help="Number of parallel analysis processes"
    ),
    include_code: bool = typer.Option(
        True,
        "--include-code/--no-code",
        help="Include code consistency analysis"
    ),
) -> None:
    """
    Perform batch analysis of multiple README files.
    
    Input file should contain one target per line:
        README.md
        https://github.com/user/repo1
        ./project1
        ./project2/README.md
    """
    
    try:
        # Load configuration
        config = load_configuration(config_file)
        
        # Read targets from file
        targets = read_batch_targets(input_file)
        
        if not targets:
            console.print("[red]No valid targets found in input file[/red]")
            raise typer.Exit(1)
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Process targets
        results = process_batch_targets(targets, config, include_code, parallel)
        
        # Save individual results
        save_batch_results(results, output_dir)
        
        # Generate and save summary
        summary = generate_batch_summary(results)
        
        if summary_file:
            save_summary_report(summary, summary_file)
        
        # Display summary
        display_batch_summary(summary)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def compare(
    targets: List[str] = typer.Argument(
        ...,
        help="Multiple README files or repositories to compare"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for comparison report"
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config", "-c",
        help="Configuration file path"
    ),
) -> None:
    """
    Compare quality scores across multiple README files.
    
    Example:
        readme-analyzer compare README1.md README2.md https://github.com/user/repo
    """
    
    try:
        if len(targets) < 2:
            console.print("[red]At least 2 targets required for comparison[/red]")
            raise typer.Exit(1)
        
        # Load configuration
        config = load_configuration(config_file)
        
        # Analyze all targets
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing targets...", total=len(targets))
            
            for target in targets:
                progress.update(task, description=f"Analyzing {Path(target).name}")
                
                if target.startswith(('http://', 'https://')):
                    result = analyze_github_repo(target, config, True)
                elif os.path.isfile(target):
                    result = analyze_single_file(target, None, config)
                else:
                    console.print(f"[yellow]Warning: Skipping invalid target: {target}[/yellow]")
                    continue
                
                results.append((target, result))
                progress.advance(task)
        
        # Generate comparison report
        comparison = generate_comparison_report(results)
        
        # Display comparison
        display_comparison(comparison)
        
        # Save if requested
        if output:
            save_comparison_report(comparison, output)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config_cmd(
    action: str = typer.Argument(
        ...,
        help="Action: show, create, validate"
    ),
    file: Optional[str] = typer.Option(
        None,
        "--file", "-f",
        help="Configuration file path"
    ),
) -> None:
    """
    Manage configuration files.
    
    Actions:
        show     - Display current configuration
        create   - Create sample configuration file
        validate - Validate configuration file
    """
    
    if action == "show":
        config = get_config()
        display_config(config)
        
    elif action == "create":
        if not file:
            file = "readme_quality_config.yaml"
        create_sample_config(file)
        
    elif action == "validate":
        if not file:
            console.print("[red]Configuration file path required for validation[/red]")
            raise typer.Exit(1)
        validate_config_file(file)
        
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)


def load_configuration(config_file: Optional[str]) -> Config:
    """Load configuration from file or use default."""
    if config_file:
        if not Path(config_file).exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            raise typer.Exit(1)
        return Config(config_file)
    return get_config()


def parse_weights(weights_str: str) -> Dict[str, float]:
    """Parse weights string into dictionary."""
    try:
        parts = [float(x.strip()) for x in weights_str.split(',')]
        if len(parts) != 4:
            raise ValueError("Expected 4 weight values")
        
        weight_keys = ['readability', 'structural', 'complexity', 'consistency']
        weights = dict(zip(weight_keys, parts))
        
        # Normalize to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
        
    except Exception as e:
        console.print(f"[red]Invalid weights format: {weights_str}. Expected: r,s,c,n[/red]")
        raise typer.Exit(1)


def analyze_single_file(file_path: str, repository_path: Optional[str], config: Config):
    """Analyze a single README file."""
    analyzer = ReadmeAnalyzer(config.get_analyzer_config())
    
    with console.status(f"Analyzing {Path(file_path).name}..."):
        return analyzer.analyze_file(file_path, repository_path)


def analyze_github_repo(repo_url: str, config: Config, include_code: bool):
    """Analyze README from GitHub repository."""
    github_analyzer = GitHubAnalyzer(config.server.github_token)
    
    with console.status(f"Fetching from GitHub..."):
        return github_analyzer.analyze_repository(repo_url, include_code)


def analyze_directory(dir_path: str, config: Config, include_code: bool):
    """Analyze README files in directory."""
    readme_files = find_readme_files(dir_path)
    
    if not readme_files:
        console.print(f"[yellow]No README files found in {dir_path}[/yellow]")
        return None
    
    # Use the first README found
    readme_file = readme_files[0]
    repository_path = dir_path if include_code else None
    
    return analyze_single_file(readme_file, repository_path, config)


def find_readme_files(directory: str) -> List[str]:
    """Find README files in directory."""
    readme_patterns = ['README.md', 'readme.md', 'README.rst', 'README.txt', 'README']
    found_files = []
    
    for pattern in readme_patterns:
        file_path = Path(directory) / pattern
        if file_path.exists():
            found_files.append(str(file_path))
    
    return found_files


def display_results(results, format_type: str, output_file: Optional[str], verbose: bool):
    """Display analysis results in specified format."""
    
    if format_type == "json":
        output_json = results.to_json()
        
        if output_file:
            Path(output_file).write_text(output_json)
            console.print(f"[green]Results saved to {output_file}[/green]")
        else:
            console.print(output_json)
            
    elif format_type == "table":
        display_table_format(results)
        
    elif format_type == "summary":
        display_summary_format(results)
        
    else:  # rich format (default)
        display_rich_format(results, verbose)
    
    # Save to file if requested and not JSON
    if output_file and format_type != "json":
        with open(output_file, 'w') as f:
            f.write(results.to_json())
        console.print(f"[green]Detailed results saved to {output_file}[/green]")


def display_rich_format(results, verbose: bool):
    """Display results in rich console format."""
    
    # Main quality score panel
    score_color = get_score_color(results.quality.overall_score)
    score_panel = Panel(
        f"[bold {score_color}]{results.quality.overall_score:.1f}/100 ({results.quality.grade_level})[/bold {score_color}]",
        title="[bold]Overall Quality Score[/bold]",
        expand=False
    )
    console.print(score_panel)
    
    # Dimension scores table
    scores_table = Table(title="Dimension Scores")
    scores_table.add_column("Dimension", style="cyan", no_wrap=True)
    scores_table.add_column("Score", justify="right", style="magenta")
    scores_table.add_column("Status", justify="center")
    
    dimensions = [
        ("Readability", results.quality.readability_score),
        ("Structure", results.quality.structural_score),
        ("Complexity", results.quality.complexity_score),
        ("Consistency", results.quality.consistency_score),
    ]
    
    for name, score in dimensions:
        color = get_score_color(score)
        status = get_score_status(score)
        scores_table.add_row(
            name,
            f"[{color}]{score:.1f}[/{color}]",
            f"[{color}]{status}[/{color}]"
        )
    
    console.print(scores_table)
    
    # Key metrics
    if verbose:
        display_detailed_metrics(results)
    
    # Recommendations
    if results.quality.recommendations:
        recs_panel = Panel(
            "\n".join(f"• {rec}" for rec in results.quality.recommendations[:5]),
            title="[bold yellow]Top Recommendations[/bold yellow]",
            border_style="yellow"
        )
        console.print(recs_panel)
    
    # Strengths and weaknesses
    if results.quality.strengths:
        strengths_text = "\n".join(f"✓ {strength}" for strength in results.quality.strengths)
        strengths_panel = Panel(
            strengths_text,
            title="[bold green]Strengths[/bold green]",
            border_style="green"
        )
        console.print(strengths_panel)
    
    if results.quality.weaknesses:
        weaknesses_text = "\n".join(f"⚠ {weakness}" for weakness in results.quality.weaknesses)
        weaknesses_panel = Panel(
            weaknesses_text,
            title="[bold red]Areas for Improvement[/bold red]",
            border_style="red"
        )
        console.print(weaknesses_panel)


def display_detailed_metrics(results):
    """Display detailed metrics in verbose mode."""
    
    # Readability details
    readability_table = Table(title="Readability Metrics", show_header=True)
    readability_table.add_column("Metric", style="cyan")
    readability_table.add_column("Value", justify="right", style="green")
    
    readability_metrics = [
        ("Word Count", results.readability.word_count),
        ("Flesch Reading Ease", f"{results.readability.flesch_reading_ease:.1f}"),
        ("Grade Level", f"{results.readability.average_grade_level:.1f}"),
        ("Readability", results.readability.readability_consensus),
    ]
    
    for metric, value in readability_metrics:
        readability_table.add_row(metric, str(value))
    
    console.print(readability_table)
    
    # Structure details
    structure_info = f"""Sections: {results.structure.section_count}
Completeness: {results.structure.completeness_score:.1f}%
Organization: {results.structure.organization_score:.1f}%"""
    
    structure_panel = Panel(structure_info, title="Structure Details")
    console.print(structure_panel)


def display_table_format(results):
    """Display results in simple table format."""
    table = Table(title="README Quality Analysis")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="magenta")
    
    table.add_row("Overall Score", f"{results.quality.overall_score:.1f}/100")
    table.add_row("Grade", results.quality.grade_level)
    table.add_row("Readability", f"{results.quality.readability_score:.1f}")
    table.add_row("Structure", f"{results.quality.structural_score:.1f}")
    table.add_row("Complexity", f"{results.quality.complexity_score:.1f}")
    table.add_row("Consistency", f"{results.quality.consistency_score:.1f}")
    
    console.print(table)


def display_summary_format(results):
    """Display results in summary format."""
    summary = f"""README Quality Summary
=====================
Overall Score: {results.quality.overall_score:.1f}/100 ({results.quality.grade_level})
Word Count: {results.readability.word_count}
Readability: {results.readability.readability_consensus}
Structure Score: {results.structure.completeness_score:.1f}%
Analysis Time: {results.analysis_duration_ms:.0f}ms

Top Recommendations:
{chr(10).join(f"• {rec}" for rec in results.quality.recommendations[:3])}"""
    
    console.print(summary)


def get_score_color(score: float) -> str:
    """Get color for score display."""
    if score >= 90:
        return "bright_green"
    elif score >= 75:
        return "green"
    elif score >= 60:
        return "yellow"
    elif score >= 45:
        return "orange3"
    else:
        return "red"


def get_score_status(score: float) -> str:
    """Get status text for score."""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 45:
        return "Poor"
    else:
        return "Critical"


# Additional functions for batch processing, comparison, etc. would continue...
# For brevity, showing the core structure and main analyze command implementation

if __name__ == "__main__":
    app()