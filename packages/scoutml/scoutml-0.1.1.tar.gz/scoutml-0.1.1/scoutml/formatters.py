"""Output formatters for ScoutML CLI."""

import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, BarColumn, TextColumn
from rich.tree import Tree
from rich import box


def format_paper_table(
    papers: List[Dict[str, Any]],
    console: Console,
    show_scores: bool = False,
    show_benchmarks: bool = False
):
    """Format papers as a rich table."""
    table = Table(
        title="Search Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title_style="bold",
        caption=f"Showing {len(papers)} papers",
        caption_style="dim"
    )
    
    # Add columns
    table.add_column("Title", style="white", overflow="fold", max_width=50)
    table.add_column("Year", style="yellow", justify="center")
    table.add_column("Citations", style="green", justify="right")
    if show_scores:
        table.add_column("Score", style="magenta", justify="right")
    table.add_column("Authors", style="dim white", overflow="ellipsis", max_width=30)
    table.add_column("ArXiv", style="cyan")
    
    # Add rows
    for paper in papers:
        row = [
            paper.get('title', paper.get('parsed_title', 'Unknown')),
            str(paper.get('year', 'N/A')),
            str(paper.get('citation_count', paper.get('citationcount', 0))),
        ]
        
        if show_scores:
            score = paper.get('score', 0)
            row.append(f"{score:.3f}")
        
        # Format authors
        authors = paper.get('authors', paper.get('parsed_authors', []))
        if isinstance(authors, list) and authors:
            if len(authors) > 2:
                author_str = f"{authors[0]} et al."
            else:
                author_str = ", ".join(str(a) for a in authors)
        else:
            author_str = str(authors) if authors else "Unknown"
        row.append(author_str)
        
        row.append(paper.get('arxiv_id', paper.get('ArXiv', 'N/A')))
        
        table.add_row(*row)
        
        # Add benchmark info if requested
        if show_benchmarks and paper.get('benchmark_info'):
            bench = paper['benchmark_info']
            bench_str = f"  → {bench['dataset']}: "
            bench_str += ", ".join(f"{m}={r}" for m, r in zip(bench['metrics'][:2], bench['results'][:2]))
            table.add_row("", "", "", bench_str, "", "")
    
    console.print(table)


def format_comparison_output(
    results: Dict[str, Any],
    console: Console,
    output_format: str = 'rich'
):
    """Format paper comparison results."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    papers = results['papers']
    comparison = results['comparison']
    matrix = results['comparison_matrix']
    
    if output_format == 'markdown':
        # Generate markdown
        md_content = f"# Paper Comparison\n\n"
        md_content += f"Comparing {len(papers)} papers:\n\n"
        
        for i, paper in enumerate(papers, 1):
            md_content += f"{i}. **{paper['parsed_title']}** ({paper['year']})\n"
            md_content += f"   - ArXiv: {paper['ArXiv']}\n"
            md_content += f"   - Citations: {paper['citationcount']}\n\n"
        
        md_content += "## Analysis\n\n"
        md_content += comparison['comparison_text']
        
        console.print(Markdown(md_content))
        return
    
    # Rich output
    console.print(Panel.fit(
        f"[bold cyan]Comparing {len(papers)} Papers[/bold cyan]",
        border_style="cyan"
    ))
    
    # Show paper list
    for i, paper in enumerate(papers, 1):
        console.print(f"\n[bold]{i}.[/bold] {paper['parsed_title']} [dim]({paper['year']})[/dim]")
        console.print(f"   ArXiv: [cyan]{paper['ArXiv']}[/cyan] | Citations: [green]{paper['citationcount']}[/green]")
    
    # Show comparison matrix
    console.print("\n[bold]Comparison Matrix:[/bold]")
    
    # Methods comparison
    console.print("\n[yellow]Methods:[/yellow]")
    for paper_id, methods in matrix['methods'].items():
        console.print(f"  {paper_id}: {', '.join(methods[:5])}")
    
    # Datasets comparison
    console.print("\n[yellow]Datasets:[/yellow]")
    for paper_id, datasets in matrix['datasets'].items():
        console.print(f"  {paper_id}: {', '.join(datasets[:5])}")
    
    # Show AI analysis
    console.print("\n[bold]AI Analysis:[/bold]")
    console.print(Panel(
        comparison['comparison_text'][:1500] + "..." if len(comparison['comparison_text']) > 1500 else comparison['comparison_text'],
        title="Detailed Comparison",
        border_style="green"
    ))


def format_review_output(
    results: Dict[str, Any],
    console: Console,
    output_format: str = 'rich'
):
    """Format literature review results."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    topic = results['topic']
    synthesis = results['synthesis']
    key_papers = results.get('key_papers', [])
    timeline = results.get('timeline', {})
    
    if output_format == 'markdown':
        # Generate full markdown review
        md_content = f"# Literature Review: {topic}\n\n"
        md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        md_content += f"**Papers analyzed:** {synthesis['papers_analyzed']}\n"
        md_content += f"**Time span:** {synthesis['year_range']}\n\n"
        md_content += synthesis['review_text']
        
        console.print(Markdown(md_content))
        return
    
    # Rich output
    console.print(Panel.fit(
        f"[bold cyan]Literature Review: {topic}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Stats
    console.print(f"\n[bold]Analysis Summary:[/bold]")
    console.print(f"• Papers analyzed: [green]{synthesis['papers_analyzed']}[/green]")
    console.print(f"• Year range: [yellow]{synthesis['year_range']}[/yellow]")
    # Handle key methods properly
    key_methods = synthesis.get('key_methods', [])
    if isinstance(key_methods, list) and key_methods:
        methods_display = ', '.join(str(m) for m in key_methods[:5] if m)
    else:
        methods_display = 'N/A'
    console.print(f"• Key methods: {methods_display}")
    
    # Timeline
    if timeline:
        console.print("\n[bold]Research Timeline:[/bold]")
        tree = Tree("📅 Papers by Year")
        for year in sorted(timeline.keys(), reverse=True)[:5]:
            year_node = tree.add(f"[yellow]{year}[/yellow] ({timeline[year]['count']} papers)")
            for paper_title in timeline[year]['key_papers'][:2]:
                year_node.add(f"• {paper_title[:60]}...")
        console.print(tree)
    
    # Key papers
    if key_papers:
        console.print("\n[bold]Top 5 Key Papers:[/bold]")
        for i, paper in enumerate(key_papers[:5], 1):
            console.print(f"\n[bold]{i}.[/bold] {paper['parsed_title']}")
            console.print(f"   [dim]Citations: {paper['citationcount']} | Year: {paper['year']}[/dim]")
            # Handle methods properly
            methods = paper.get('methods', [])
            if isinstance(methods, list) and methods:
                methods_str = ', '.join(str(m) for m in methods[:3] if m)
            else:
                methods_str = 'N/A'
            console.print(f"   [dim]Methods: {methods_str}[/dim]")
    
    # Review text
    console.print("\n[bold]Literature Review:[/bold]")
    console.print(Panel(
        synthesis['review_text'][:2000] + "..." if len(synthesis['review_text']) > 2000 else synthesis['review_text'],
        title="Review Extract",
        border_style="green",
        padding=(1, 2)
    ))


def format_insights_output(
    results: Dict[str, Any],
    console: Console,
    insight_type: str,
    output_format: str = 'rich'
):
    """Format research insights output."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    if output_format == 'csv':
        # Extract relevant data for CSV based on insight type
        if insight_type == 'reproducibility':
            csv_content = export_to_csv(results.get('papers', []))
        elif insight_type == 'compute':
            # Convert trends to CSV
            trends = results.get('yearly_trends', [])
            csv_content = trends_to_csv(trends)
        else:  # funding
            sources = results.get('top_funding_sources', [])
            csv_content = funding_to_csv(sources)
        
        console.print(csv_content)
        return
    
    # Rich output based on insight type
    if insight_type == 'reproducibility':
        _format_reproducibility_insights(results, console)
    elif insight_type == 'compute':
        _format_compute_insights(results, console)
    else:  # funding
        _format_funding_insights(results, console)


def _format_reproducibility_insights(results: Dict[str, Any], console: Console):
    """Format reproducibility insights."""
    console.print(Panel.fit(
        "[bold cyan]Reproducibility Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Score distribution
    console.print("\n[bold]Score Distribution:[/bold]")
    dist = results.get('score_distribution', {})
    for score, count in dist.items():
        bar = "█" * int(count / max(dist.values()) * 30)
        console.print(f"  {score:>8}: {bar} {count}")
    
    # Top methods
    console.print("\n[bold]Most Reproducible Methods:[/bold]")
    for method in results.get('top_reproducible_methods', [])[:5]:
        console.print(f"  • {method['method']}: avg score {method['avg_score']:.2f} ({method['paper_count']} papers)")
    
    # Papers
    console.print(f"\n[bold]Top Reproducible Papers:[/bold] (Total: {results.get('total_count', 0)})")
    format_paper_table(results.get('papers', [])[:10], console)


def _format_compute_insights(results: Dict[str, Any], console: Console):
    """Format compute requirement insights."""
    console.print(Panel.fit(
        "[bold cyan]Compute Requirements Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Data quality note
    if results.get('data_quality_note'):
        console.print(f"\n[yellow]Note:[/yellow] {results['data_quality_note']}")
    
    # Overall stats
    if results.get('overall_gpu_stats'):
        stats = results['overall_gpu_stats']
        console.print("\n[bold]Overall GPU Statistics:[/bold]")
        console.print(f"  • Min GPUs: [green]{stats['min']}[/green]")
        console.print(f"  • Max GPUs: [red]{stats['max']}[/red]")
        console.print(f"  • Average: [yellow]{stats['avg']:.1f}[/yellow]")
        if 'median' in stats:
            console.print(f"  • Median: [blue]{stats['median']}[/blue]")
    
    # GPU types
    console.print("\n[bold]Popular GPU Types:[/bold]")
    for gpu_type, count in list(results.get('gpu_type_popularity', {}).items())[:5]:
        console.print(f"  • {gpu_type}: {count} papers")
    
    # Yearly trends
    if results.get('yearly_trends'):
        console.print("\n[bold]Recent Trends:[/bold]")
        for trend in results['yearly_trends'][-3:]:
            console.print(f"\n  [yellow]{trend['year']}:[/yellow]")
            console.print(f"    Papers: {trend['total_papers']} (with GPU info: {trend['papers_with_gpu_info']})")
            if trend.get('gpu_count_stats'):
                console.print(f"    Avg GPUs: {trend['gpu_count_stats']['avg']:.1f}")


def _format_funding_insights(results: Dict[str, Any], console: Console):
    """Format funding analysis insights."""
    console.print(Panel.fit(
        "[bold cyan]Funding Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Data quality note
    if results.get('data_quality_note'):
        console.print(f"\n[yellow]Note:[/yellow] {results['data_quality_note']}")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Total funded papers: {results.get('total_funded_papers', 0)}")
    console.print(f"  • Unique funding sources: {results.get('unique_funding_sources', 0)}")
    
    # Top sources
    console.print("\n[bold]Top Funding Sources by Impact:[/bold]")
    table = Table(box=box.SIMPLE)
    table.add_column("Source", style="cyan")
    table.add_column("Papers", justify="right")
    table.add_column("Avg Citations", justify="right")
    table.add_column("SOTA %", justify="right")
    
    for source in results.get('top_funding_sources', [])[:10]:
        table.add_row(
            source['source'][:40],
            str(source['paper_count']),
            f"{source['avg_citations']:.1f}",
            f"{source['sota_percentage']:.1f}%"
        )
    
    console.print(table)


# Export functions
def export_to_csv(papers: List[Dict[str, Any]]) -> str:
    """Export papers to CSV format."""
    output = io.StringIO()
    if not papers:
        return ""
    
    # Define fields to export
    fields = ['parsed_title', 'year', 'citationcount', 'ArXiv', 'venue', 
              'parsed_authors', 'methods', 'datasets', 'sota_status']
    
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    
    for paper in papers:
        # Convert lists to strings
        row = paper.copy()
        if 'parsed_authors' in row and isinstance(row['parsed_authors'], list):
            row['parsed_authors'] = '; '.join(row['parsed_authors'])
        if 'methods' in row and isinstance(row['methods'], list):
            row['methods'] = '; '.join(row['methods'])
        if 'datasets' in row and isinstance(row['datasets'], list):
            row['datasets'] = '; '.join(row['datasets'])
        
        writer.writerow(row)
    
    return output.getvalue()


def export_to_json(data: Any, filepath: str):
    """Export data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_markdown(papers: List[Dict[str, Any]]) -> str:
    """Export papers to markdown format."""
    md = "# Search Results\n\n"
    
    for i, paper in enumerate(papers, 1):
        md += f"## {i}. {paper.get('parsed_title', 'Unknown')}\n\n"
        md += f"- **Year**: {paper.get('year', 'N/A')}\n"
        md += f"- **Citations**: {paper.get('citationcount', 0)}\n"
        md += f"- **ArXiv**: {paper.get('ArXiv', 'N/A')}\n"
        
        authors = paper.get('parsed_authors', [])
        if authors:
            md += f"- **Authors**: {', '.join(authors[:5])}\n"
        
        if paper.get('abstract'):
            md += f"\n**Abstract**: {paper['abstract'][:300]}...\n"
        
        md += "\n---\n\n"
    
    return md


def trends_to_csv(trends: List[Dict[str, Any]]) -> str:
    """Convert trend data to CSV."""
    output = io.StringIO()
    if not trends:
        return ""
    
    writer = csv.writer(output)
    writer.writerow(['Year', 'Total Papers', 'Papers with GPU Info', 'Avg GPUs', 'Top GPU Type'])
    
    for trend in trends:
        gpu_stats = trend.get('gpu_count_stats', {})
        top_gpu = list(trend.get('top_gpu_types', {}).keys())[0] if trend.get('top_gpu_types') else 'N/A'
        
        writer.writerow([
            trend['year'],
            trend['total_papers'],
            trend['papers_with_gpu_info'],
            f"{gpu_stats.get('avg', 0):.1f}" if gpu_stats else 'N/A',
            top_gpu
        ])
    
    return output.getvalue()


def funding_to_csv(sources: List[Dict[str, Any]]) -> str:
    """Convert funding data to CSV."""
    output = io.StringIO()
    if not sources:
        return ""
    
    writer = csv.DictWriter(output, fieldnames=['source', 'paper_count', 'avg_citations', 'sota_percentage'])
    writer.writeheader()
    writer.writerows(sources)
    
    return output.getvalue()


def format_implementation_guide(guide: Dict[str, Any], console: Console):
    """Format implementation guide output."""
    console.print(f"\n[bold cyan]Implementation Guide for:[/bold cyan] {guide['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {guide['paper_info']['arxiv_id']}[/dim]")
    console.print(f"[dim]Complexity: {guide['paper_info']['complexity'].upper()}[/dim]\n")
    
    # Prerequisites
    console.print("[bold]Prerequisites:[/bold]")
    for prereq in guide['prerequisites']:
        console.print(f"\n  [cyan]{prereq['category']}:[/cyan]")
        for item in prereq['items']:
            console.print(f"    • {item}")
    
    # Implementation roadmap
    console.print("\n[bold]Implementation Roadmap:[/bold]")
    for phase in guide['implementation_roadmap']['phases']:
        console.print(f"\n  [bold cyan]Phase {phase['phase']}: {phase['name']}[/bold cyan] ({phase['duration']})")
        for task in phase['tasks']:
            console.print(f"    ✓ {task}")
    
    # Key components
    console.print("\n[bold]Key Components:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Type")
    table.add_column("Critical", style="red")
    table.add_column("Notes")
    
    for comp in guide['key_components']:
        table.add_row(
            comp['name'],
            comp['type'],
            "Yes" if comp['critical'] else "No",
            comp['implementation_notes']
        )
    console.print(table)
    
    # Time estimate
    time_est = guide['estimated_time']
    console.print(f"\n[bold]Estimated Time:[/bold]")
    console.print(f"  Minimum: {time_est['minimum_days']} days")
    console.print(f"  Expected: {time_est['expected_days']} days")
    console.print(f"  Maximum: {time_est['maximum_days']} days")
    
    # Resources
    if guide.get('reference_implementations'):
        console.print("\n[bold]Reference Implementations:[/bold]")
        for ref in guide['reference_implementations'][:3]:
            console.print(f"  • {ref['title']}")
            console.print(f"    [dim]{ref['code_url']}[/dim]")


def format_research_critique(critique: Dict[str, Any], console: Console):
    """Format research critique output."""
    console.print(f"\n[bold cyan]Research Critique:[/bold cyan] {critique['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {critique['paper_info']['arxiv_id']} | Year: {critique['paper_info']['year']} | Citations: {critique['paper_info']['citations']}[/dim]\n")
    
    # Overall assessment
    assessment = critique['overall_assessment']
    scores = assessment['scores']
    
    console.print("[bold]Overall Assessment:[/bold]")
    console.print(f"  Recommendation: [bold]{assessment['recommendation']}[/bold]")
    console.print(f"  Scores: Novelty={scores['novelty']}/10 | Impact={scores['impact']}/10 | Technical={scores['technical_quality']}/10 | Overall={scores['overall']}/10")
    
    # Strengths and weaknesses
    console.print("\n[bold green]Strengths:[/bold green]")
    for strength in assessment['strengths']:
        console.print(f"  ✓ {strength}")
    
    console.print("\n[bold red]Weaknesses:[/bold red]")
    for weakness in assessment['weaknesses']:
        console.print(f"  ✗ {weakness}")
    
    # Detailed critique
    for aspect, details in critique['detailed_critique'].items():
        console.print(f"\n[bold]{aspect.title()} Analysis:[/bold]")
        
        if details.get('strengths'):
            console.print("  [green]Strengths:[/green]")
            for s in details['strengths']:
                console.print(f"    • {s}")
        
        if details.get('weaknesses'):
            console.print("  [red]Weaknesses:[/red]")
            for w in details['weaknesses']:
                console.print(f"    • {w}")
        
        if details.get('suggestions'):
            console.print("  [yellow]Suggestions:[/yellow]")
            for s in details['suggestions']:
                console.print(f"    → {s}")
    
    # Improvement suggestions
    if critique.get('improvement_suggestions'):
        console.print("\n[bold]Top Improvement Suggestions:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Category")
        table.add_column("Suggestion")
        table.add_column("Priority")
        table.add_column("Effort")
        
        for sugg in critique['improvement_suggestions'][:5]:
            table.add_row(
                str(sugg['id']),
                sugg['category'],
                sugg['suggestion'],
                sugg['priority'].upper(),
                sugg['effort'].title()
            )
        console.print(table)


def format_limitation_solutions(solutions: Dict[str, Any], console: Console):
    """Format limitation solutions output."""
    console.print(f"\n[bold cyan]Limitation Solutions for:[/bold cyan] {solutions['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {solutions['paper_info']['arxiv_id']}[/dim]\n")
    
    # Identified limitations
    console.print("[bold]Identified Limitations:[/bold]")
    for lim in solutions['identified_limitations']:
        severity_color = {"high": "red", "medium": "yellow", "low": "green"}[lim['severity']]
        console.print(f"\n  [{severity_color}]{lim['severity'].upper()}[/{severity_color}] - {lim['category'].title()}")
        console.print(f"  {lim['description']}")
    
    # Solutions for each limitation
    console.print("\n[bold]Proposed Solutions:[/bold]")
    for sol_set in solutions['solutions']:
        lim = sol_set['limitation']
        console.print(f"\n[bold cyan]For: {lim['description']}[/bold cyan]")
        
        for i, solution in enumerate(sol_set['proposed_solutions'], 1):
            console.print(f"\n  {i}. [bold]{solution['approach']}[/bold]")
            console.print(f"     {solution['description']}")
            console.print(f"     [dim]Tradeoff: {solution['tradeoff']}[/dim]")
            console.print(f"     [dim]Complexity: {solution['implementation_complexity']} | Expected: {solution['expected_improvement']}[/dim]")
            
            if solution.get('techniques'):
                console.print("     Techniques:")
                for tech in solution['techniques']:
                    console.print(f"       • {tech}")
    
    # Cross-paper solutions
    if solutions.get('cross_paper_solutions'):
        console.print("\n[bold]Cross-Paper Solutions:[/bold]")
        for cross_sol in solutions['cross_paper_solutions']:
            console.print(f"\n  {cross_sol['solution']}")
            console.print("  Related papers:")
            for paper in cross_sol['papers'][:3]:
                console.print(f"    • {paper['title']} ({paper['arxiv_id']})")


def format_experiment_design(design: Dict[str, Any], console: Console):
    """Format experiment design output."""
    console.print(f"\n[bold cyan]Experiment Design[/bold cyan]")
    console.print(f"[bold]Paper:[/bold] {design['paper_info']['title']}")
    console.print(f"[bold]Hypothesis:[/bold] {design['hypothesis']}\n")
    
    # Experiment plan
    plan = design['experiment_plan']
    console.print(f"[bold]Experiment Type:[/bold] {plan['experiment_type'].replace('_', ' ').title()}")
    
    console.print("\n[bold]Execution Plan:[/bold]")
    for phase in plan['phases']:
        console.print(f"\n  [bold cyan]Phase {phase['phase']}: {phase['name']}[/bold cyan] ({phase['duration']})")
        for task in phase['tasks']:
            console.print(f"    • {task}")
    
    # Baselines
    console.print("\n[bold]Baselines:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Baseline", style="cyan")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Description")
    
    for baseline in design['baselines']:
        table.add_row(
            baseline['name'],
            baseline['type'],
            baseline['implementation_status'],
            baseline['description'][:50] + "..." if len(baseline['description']) > 50 else baseline['description']
        )
    console.print(table)
    
    # Evaluation protocol
    protocol = design['evaluation_protocol']
    console.print("\n[bold]Evaluation Protocol:[/bold]")
    console.print(f"  Primary metrics: {', '.join(protocol['primary_metrics'])}")
    console.print(f"  Secondary metrics: {', '.join(protocol['secondary_metrics'])}")
    console.print(f"  Datasets: {', '.join(protocol['datasets'])}")
    
    # Expected outcomes
    outcomes = design['expected_outcomes']
    console.print("\n[bold]Expected Outcomes:[/bold]")
    console.print("  Success criteria:")
    for criterion in outcomes['success_criteria']:
        console.print(f"    ✓ {criterion}")
    
    # Risk analysis
    risks = design['risk_analysis']
    risk_color = {"high": "red", "medium": "yellow", "low": "green"}[risks['overall_risk_level']]
    console.print(f"\n[bold]Risk Analysis:[/bold] [{risk_color}]{risks['overall_risk_level'].upper()} RISK[/{risk_color}]")
    
    all_risks = risks['technical_risks'] + risks['resource_risks'] + risks['timeline_risks']
    if all_risks:
        for risk in all_risks[:3]:  # Show top 3 risks
            impact_color = {"high": "red", "medium": "yellow", "low": "green"}[risk['impact']]
            console.print(f"  • {risk['risk']} ([{impact_color}]{risk['impact']}[/{impact_color}])")
            console.print(f"    Mitigation: {risk['mitigation']}")
    
    # Timeline
    timeline = design['timeline']
    console.print(f"\n[bold]Timeline:[/bold] {timeline['total_duration']}")
    console.print("  Key milestones:")
    for milestone in timeline['milestones'][:4]:
        console.print(f"    Week {milestone['week']}: {milestone['milestone']}")