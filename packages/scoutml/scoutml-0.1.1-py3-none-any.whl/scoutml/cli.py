"""Main CLI entry point for ScoutML."""

import sys
import json
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from tabulate import tabulate

from .client import ScoutMLClient
from .config import Config
from .exceptions import ScoutMLError, AuthenticationError, NotFoundError
from .formatters import (
    format_paper_table,
    format_comparison_output,
    format_review_output,
    format_insights_output,
    export_to_csv,
    export_to_json,
    export_to_markdown,
    format_implementation_guide,
    format_research_critique,
    format_limitation_solutions,
    format_experiment_design
)

console = Console()


def get_client(use_local: bool = False) -> ScoutMLClient:
    """Get configured client instance."""
    config = Config()
    
    # Override API URL if --local flag is used
    if use_local:
        config.api_url = "http://localhost:8000"
        console.print("[dim]Using local server: http://localhost:8000[/dim]")
    
    if not config.is_configured:
        console.print("[red]Error: API key not configured![/red]")
        console.print("\nPlease set your API key using one of these methods:")
        console.print("1. Export environment variable: [cyan]export SCOUTML_API_KEY='your-key'[/cyan]")
        console.print("2. Create .env file with: [cyan]SCOUTML_API_KEY=your-key[/cyan]")
        console.print("3. Use configure command: [cyan]scoutml configure --api-key your-key[/cyan]")
        sys.exit(1)
    
    return ScoutMLClient(config)


@click.group()
@click.version_option()
@click.option('--local', is_flag=True, help='Use local development server (localhost:8000)')
@click.pass_context
def cli(ctx, local):
    """ScoutML - Scout ML Research Papers
    
    Discover, analyze, and implement ML research with intelligent agents.
    """
    ctx.ensure_object(dict)
    ctx.obj['local'] = local


# Configuration command
@cli.command()
@click.option('--api-key', prompt=True, hide_input=True, help='Your ScoutML API key')
def configure(api_key: str):
    """Configure ScoutML CLI with your API key."""
    config = Config()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Saving configuration...", total=1)
        
        try:
            config.save_api_key(api_key)
            progress.update(task, completed=1)
            
            console.print("[green]✓ Configuration saved successfully![/green]")
            console.print(f"API key: [dim]{api_key[:8]}...{api_key[-4:]}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Error saving configuration: {str(e)}[/red]")
            sys.exit(1)


# Search commands
@cli.command()
@click.argument('query')
@click.option('--limit', default=20, help='Number of results')
@click.option('--year-min', type=int, help='Minimum publication year')
@click.option('--year-max', type=int, help='Maximum publication year')
@click.option('--min-citations', type=int, help='Minimum citation count')
@click.option('--venue', help='Filter by venue')
@click.option('--sota-only', is_flag=True, help='Only SOTA papers')
@click.option('--domain', help='Filter by domain')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), default='table')
@click.option('--export', type=click.Path(), help='Export results to file')
@click.pass_context
def search(ctx, query: str, limit: int, year_min: Optional[int], year_max: Optional[int],
          min_citations: Optional[int], venue: Optional[str], sota_only: bool,
          domain: Optional[str], output: str, export: Optional[str]):
    """Perform semantic search on research papers."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status(f"Searching for '{query}'..."):
        try:
            results = client.semantic_search(
                query=query,
                limit=limit,
                year_min=year_min,
                year_max=year_max,
                min_citations=min_citations,
                venue=venue,
                sota_only=sota_only,
                domain=domain
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    # Display results
    papers = results.get('results', [])
    total = results.get('count', 0)
    
    console.print(f"\n[bold]Found {total} papers[/bold] (showing {len(papers)})")
    
    if results.get('query_info', {}).get('filters_applied'):
        console.print("Filters applied:", results['query_info']['filters_applied'])
    
    if output == 'table':
        format_paper_table(papers, console)
    elif output == 'json':
        console.print_json(json.dumps(papers, indent=2))
    else:  # csv
        csv_content = export_to_csv(papers)
        console.print(csv_content)
    
    # Export if requested
    if export:
        if output == 'json':
            export_to_json(papers, export)
        elif output == 'csv':
            with open(export, 'w') as f:
                f.write(export_to_csv(papers))
        else:
            with open(export, 'w') as f:
                f.write(export_to_markdown(papers))
        console.print(f"[green]Results exported to {export}[/green]")


@cli.command('method-search')
@click.argument('method')
@click.option('--limit', default=20, help='Number of results')
@click.option('--sort-by', type=click.Choice(['citations', 'year', 'novelty']), default='citations')
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), default='table')
@click.pass_context
def method_search(ctx, method: str, limit: int, sort_by: str, year_min: Optional[int],
                 year_max: Optional[int], output: str):
    """Search papers using a specific method or technique."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status(f"Searching for papers using '{method}'..."):
        try:
            results = client.method_search(
                method=method,
                limit=limit,
                sort_by=sort_by,
                year_min=year_min,
                year_max=year_max
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    papers = results.get('results', [])
    total = results['query_info']['total_papers_with_method']
    
    console.print(f"\n[bold]Found {total} papers using '{method}'[/bold]")
    console.print(f"Sorted by: {sort_by}")
    
    if output == 'table':
        format_paper_table(papers, console)
    elif output == 'json':
        console.print_json(json.dumps(papers, indent=2))
    else:
        console.print(export_to_csv(papers))


@cli.command('dataset-search')
@click.argument('dataset')
@click.option('--limit', default=20, help='Number of results')
@click.option('--include-benchmarks/--no-benchmarks', default=True)
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), default='table')
@click.pass_context
def dataset_search(ctx, dataset: str, limit: int, include_benchmarks: bool,
                  year_min: Optional[int], year_max: Optional[int], output: str):
    """Search papers using a specific dataset."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status(f"Searching for papers using '{dataset}'..."):
        try:
            results = client.dataset_search(
                dataset=dataset,
                limit=limit,
                include_benchmarks=include_benchmarks,
                year_min=year_min,
                year_max=year_max
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    papers = results.get('results', [])
    total = results['query_info']['total_papers_using_dataset']
    
    console.print(f"\n[bold]Found {total} papers using '{dataset}'[/bold]")
    
    if output == 'table':
        format_paper_table(papers, console, show_benchmarks=include_benchmarks)
    elif output == 'json':
        console.print_json(json.dumps(papers, indent=2))
    else:
        console.print(export_to_csv(papers))


# Analysis commands
@cli.command()
@click.argument('paper_ids', nargs=-1, required=True)
@click.option('--from-file', type=click.Path(exists=True), help='Read paper IDs from file')
@click.option('--output', type=click.Choice(['rich', 'json', 'markdown']), default='rich')
@click.pass_context
def compare(ctx, paper_ids: tuple, from_file: Optional[str], output: str):
    """Compare multiple papers side by side."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    # Get paper IDs
    if from_file:
        with open(from_file, 'r') as f:
            ids = [line.strip() for line in f if line.strip()]
    else:
        ids = list(paper_ids)
    
    if len(ids) < 2:
        console.print("[red]Error: At least 2 paper IDs required[/red]")
        sys.exit(1)
    
    if len(ids) > 10:
        console.print("[red]Error: Maximum 10 papers can be compared[/red]")
        sys.exit(1)
    
    with console.status(f"Comparing {len(ids)} papers..."):
        try:
            results = client.compare_papers(ids)
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    format_comparison_output(results, console, output_format=output)


@cli.command()
@click.argument('topic')
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--min-citations', default=0, help='Minimum citations')
@click.option('--limit', default=50, help='Max papers to analyze')
@click.option('--output', type=click.Choice(['rich', 'markdown', 'json']), default='rich')
@click.option('--export', type=click.Path(), help='Export review to file')
@click.pass_context
def review(ctx, topic: str, year_min: Optional[int], year_max: Optional[int],
          min_citations: int, limit: int, output: str, export: Optional[str]):
    """Generate a literature review on a topic."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status(f"Generating literature review on '{topic}'..."):
        try:
            results = client.generate_literature_review(
                topic=topic,
                year_min=year_min,
                year_max=year_max,
                min_citations=min_citations,
                limit=limit
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    format_review_output(results, console, output_format=output)
    
    if export:
        if output == 'markdown' or export.endswith('.md'):
            content = results['synthesis']['review_text']
        else:
            content = json.dumps(results, indent=2)
        
        with open(export, 'w') as f:
            f.write(content)
        console.print(f"\n[green]Review exported to {export}[/green]")


@cli.command()
@click.option('--paper-id', help='ArXiv ID of source paper')
@click.option('--abstract', help='Abstract text to match')
@click.option('--abstract-file', type=click.Path(exists=True), help='File containing abstract')
@click.option('--limit', default=10, help='Number of results')
@click.option('--threshold', default=0.7, help='Similarity threshold (0-1)')
@click.option('--output', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def similar(ctx, paper_id: Optional[str], abstract: Optional[str], abstract_file: Optional[str],
           limit: int, threshold: float, output: str):
    """Find papers similar to a given paper or abstract."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    # Get abstract text if from file
    if abstract_file:
        with open(abstract_file, 'r') as f:
            abstract = f.read().strip()
    
    if not paper_id and not abstract:
        console.print("[red]Error: Either --paper-id or --abstract required[/red]")
        sys.exit(1)
    
    if paper_id and abstract:
        console.print("[red]Error: Use either --paper-id or --abstract, not both[/red]")
        sys.exit(1)
    
    with console.status("Finding similar papers..."):
        try:
            if paper_id and not abstract:
                # Use PostgreSQL endpoint for paper-based similarity
                results = client.get_similar_papers(paper_id, limit=limit)
            else:
                # Use MongoDB endpoint for abstract-based similarity
                results = client.find_similar_papers(
                    paper_id=paper_id,
                    abstract_text=abstract,
                    limit=limit,
                    similarity_threshold=threshold
                )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    # Handle different response formats
    if 'query_paper' in results:
        # PostgreSQL response format
        console.print(f"\n[bold]Similar to:[/bold] {results['query_paper']['title']}")
        console.print(f"Found {len(results['similar_papers'])} similar papers")
    else:
        # MongoDB response format
        source = results['source']
        if source['type'] == 'paper':
            console.print(f"\n[bold]Similar to:[/bold] {source['title']}")
        else:
            console.print(f"\n[bold]Similar to abstract:[/bold] {source['abstract_preview']}")
        
        console.print(f"Found {results['count']} similar papers")
        
        # Show similarity stats
        stats = results['similarity_stats']
        console.print(f"Similarity scores: min={stats['min']:.3f}, max={stats['max']:.3f}, avg={stats['avg']:.3f}")
    
    if output == 'table':
        format_paper_table(results['similar_papers'], console, show_scores=True)
    else:
        console.print_json(json.dumps(results['similar_papers'], indent=2))


# Agent commands
@cli.group()
def agent():
    """Access intelligent research agents."""
    pass


@agent.command('implement')
@click.argument('arxiv_id')
@click.option('--framework', type=click.Choice(['pytorch', 'tensorflow', 'jax', 'other']), 
              default='pytorch', help='Target implementation framework')
@click.option('--level', type=click.Choice(['beginner', 'intermediate', 'advanced']), 
              default='intermediate', help='Experience level')
@click.option('--output', type=click.Choice(['rich', 'json']), default='rich')
@click.pass_context
def implement_guide(ctx, arxiv_id: str, framework: str, level: str, output: str):
    """Generate implementation guide for a paper."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status("Generating implementation guide..."):
        try:
            results = client.implement_guide(
                arxiv_id=arxiv_id,
                target_framework=framework,
                experience_level=level
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    if output == 'json':
        console.print_json(json.dumps(results, indent=2))
    else:
        format_implementation_guide(results, console)


@agent.command('critique')
@click.argument('arxiv_id')
@click.option('--aspects', multiple=True, 
              type=click.Choice(['methodology', 'experiments', 'claims', 'reproducibility']),
              help='Aspects to critique (can specify multiple)')
@click.option('--output', type=click.Choice(['rich', 'json']), default='rich')
@click.pass_context
def research_critique(ctx, arxiv_id: str, aspects: tuple, output: str):
    """Get comprehensive research critique."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    # Use all aspects if none specified
    critique_aspects = list(aspects) if aspects else None
    
    with console.status("Analyzing paper..."):
        try:
            results = client.research_critique(
                arxiv_id=arxiv_id,
                critique_aspects=critique_aspects
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    if output == 'json':
        console.print_json(json.dumps(results, indent=2))
    else:
        format_research_critique(results, console)


@agent.command('solve-limitations')
@click.argument('arxiv_id')
@click.option('--focus', help='Specific limitation to focus on')
@click.option('--tradeoffs', multiple=True,
              type=click.Choice(['accuracy', 'speed', 'memory', 'complexity', 'data_requirements', 'quality']),
              help='Acceptable tradeoffs (can specify multiple)')
@click.option('--output', type=click.Choice(['rich', 'json']), default='rich')
@click.pass_context
def solve_limitations(ctx, arxiv_id: str, focus: Optional[str], tradeoffs: tuple, output: str):
    """Get solutions for paper limitations."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status("Analyzing limitations..."):
        try:
            results = client.solve_limitations(
                arxiv_id=arxiv_id,
                focus_limitation=focus,
                acceptable_tradeoffs=list(tradeoffs) if tradeoffs else None
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    if output == 'json':
        console.print_json(json.dumps(results, indent=2))
    else:
        format_limitation_solutions(results, console)


@agent.command('design-experiment')
@click.argument('base_paper')
@click.argument('hypothesis')
@click.option('--gpu-hours', type=int, help='Available GPU hours')
@click.option('--datasets', multiple=True, help='Available datasets')
@click.option('--output', type=click.Choice(['rich', 'json']), default='rich')
@click.pass_context
def design_experiment(ctx, base_paper: str, hypothesis: str, gpu_hours: Optional[int], 
                     datasets: tuple, output: str):
    """Design experiment to test hypothesis."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    resources = {}
    if gpu_hours is not None:
        resources['gpu_hours'] = gpu_hours
    if datasets:
        resources['datasets'] = list(datasets)
    
    with console.status("Designing experiment..."):
        try:
            results = client.design_experiment(
                base_paper=base_paper,
                hypothesis=hypothesis,
                resources=resources
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    if output == 'json':
        console.print_json(json.dumps(results, indent=2))
    else:
        format_experiment_design(results, console)


# Insights commands
@cli.group()
def insights():
    """Access research intelligence and insights."""
    pass


@insights.command('reproducibility')
@click.option('--domain', help='Filter by domain')
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--limit', default=20, help='Number of results')
@click.option('--output', type=click.Choice(['rich', 'json', 'csv']), default='rich')
@click.pass_context
def reproducibility_insights(ctx, domain: Optional[str], year_min: Optional[int],
                           year_max: Optional[int], limit: int, output: str):
    """Analyze papers by reproducibility score."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status("Analyzing reproducibility..."):
        try:
            results = client.get_reproducibility_ranked(
                domain=domain,
                year_min=year_min,
                year_max=year_max,
                limit=limit
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    format_insights_output(results, console, insight_type='reproducibility', output_format=output)


@insights.command('compute')
@click.option('--method', help='Filter by method/technique')
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--output', type=click.Choice(['rich', 'json', 'csv']), default='rich')
@click.pass_context
def compute_insights(ctx, method: Optional[str], year_min: Optional[int],
                    year_max: Optional[int], output: str):
    """Analyze compute requirements and GPU trends."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status("Analyzing compute requirements..."):
        try:
            results = client.analyze_compute_requirements(
                method=method,
                year_min=year_min,
                year_max=year_max
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    format_insights_output(results, console, insight_type='compute', output_format=output)


@insights.command('funding')
@click.option('--institution', help='Filter by institution')
@click.option('--source', help='Filter by funding source')
@click.option('--year-min', type=int, help='Minimum year')
@click.option('--year-max', type=int, help='Maximum year')
@click.option('--limit', default=20, help='Number of top sources')
@click.option('--output', type=click.Choice(['rich', 'json', 'csv']), default='rich')
@click.pass_context
def funding_insights(ctx, institution: Optional[str], source: Optional[str],
                    year_min: Optional[int], year_max: Optional[int],
                    limit: int, output: str):
    """Analyze funding sources and their impact."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status("Analyzing funding sources..."):
        try:
            results = client.analyze_funding(
                institution=institution,
                funding_source=source,
                year_min=year_min,
                year_max=year_max,
                limit=limit
            )
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    format_insights_output(results, console, insight_type='funding', output_format=output)


# Utility commands
@cli.command()
@click.argument('arxiv_id')
@click.option('--similar/--no-similar', default=False, help='Include similar papers')
@click.option('--similar-limit', default=5, help='Number of similar papers')
@click.pass_context
def paper(ctx, arxiv_id: str, similar: bool, similar_limit: int):
    """Get detailed information about a specific paper."""
    client = get_client(use_local=ctx.obj.get('local', False))
    
    with console.status(f"Fetching paper {arxiv_id}..."):
        try:
            result = client.get_paper(arxiv_id, include_similar=similar, similar_limit=similar_limit)
        except NotFoundError:
            console.print(f"[red]Paper {arxiv_id} not found[/red]")
            sys.exit(1)
        except ScoutMLError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    paper = result['paper']
    
    # Create detailed panel
    panel_content = f"""
[bold]{paper.get('title', paper.get('parsed_title', 'Unknown'))}[/bold]

[dim]ArXiv:[/dim] {paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))}
[dim]Year:[/dim] {paper.get('year', 'N/A')}
[dim]Citations:[/dim] {paper.get('citation_count', paper.get('citationcount', 0))}
[dim]Authors:[/dim] {', '.join(paper.get('authors', paper.get('parsed_authors', []))[:3])}{'...' if len(paper.get('authors', paper.get('parsed_authors', []))) > 3 else ''}

[bold]Abstract:[/bold]
{paper.get('abstract', '')[:500]}{'...' if len(paper.get('abstract', '')) > 500 else ''}

[bold]Methods:[/bold] {', '.join(paper.get('methods', [])[:5])}
[bold]Datasets:[/bold] {', '.join(paper.get('datasets', [])[:5])}
[bold]SOTA:[/bold] {paper.get('sota_status', 'Unknown')}
"""
    
    console.print(Panel(panel_content, title="Paper Details", border_style="cyan"))
    
    if similar and 'similar_papers' in result:
        console.print("\n[bold]Similar Papers:[/bold]")
        format_paper_table(result['similar_papers'], console, show_scores=True)


if __name__ == '__main__':
    cli()