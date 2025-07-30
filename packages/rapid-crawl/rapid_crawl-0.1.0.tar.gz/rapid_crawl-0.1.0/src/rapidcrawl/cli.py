"""
Command-line interface for RapidCrawl.
"""

import sys
import json
from pathlib import Path
from typing import Optional
import os

import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from dotenv import load_dotenv

from rapidcrawl import RapidCrawlApp, __version__
from rapidcrawl.models import OutputFormat, SearchEngine

# Load environment variables
load_dotenv()

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="rapidcrawl")
@click.option("--api-key", envvar="RAPIDCRAWL_API_KEY", help="API key for authentication")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, api_key: Optional[str], debug: bool):
    """RapidCrawl - Powerful web scraping and crawling toolkit."""
    ctx.ensure_object(dict)
    ctx.obj["app"] = RapidCrawlApp(api_key=api_key, debug=debug)
    ctx.obj["debug"] = debug


@cli.command()
@click.argument("url")
@click.option(
    "--format", "-f",
    multiple=True,
    type=click.Choice(["markdown", "html", "text", "screenshot", "links"]),
    default=["markdown"],
    help="Output format(s)"
)
@click.option("--output", "-o", help="Output file path")
@click.option("--wait-for", help="CSS selector to wait for")
@click.option("--timeout", type=int, default=30000, help="Timeout in milliseconds")
@click.option("--mobile", is_flag=True, help="Use mobile viewport")
@click.option("--extract-schema", help="JSON schema for structured extraction")
@click.option("--extract-prompt", help="Natural language prompt for extraction")
@click.pass_context
def scrape(
    ctx,
    url: str,
    format: tuple,
    output: Optional[str],
    wait_for: Optional[str],
    timeout: int,
    mobile: bool,
    extract_schema: Optional[str],
    extract_prompt: Optional[str],
):
    """Scrape a single URL and convert to specified formats."""
    app = ctx.obj["app"]
    
    # Parse formats
    formats = [OutputFormat(f) for f in format]
    
    # Parse extract schema if provided
    schema = None
    if extract_schema:
        try:
            schema = json.loads(extract_schema)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON schema[/red]")
            sys.exit(1)
    
    try:
        # Scrape URL
        with console.status(f"Scraping {url}..."):
            result = app.scrape_url(
                url,
                formats=formats,
                wait_for=wait_for,
                timeout=timeout,
                mobile=mobile,
                extract_schema=schema,
                extract_prompt=extract_prompt,
            )
        
        if result.success:
            console.print(f"[green]✓[/green] Scraped successfully in {result.load_time:.2f}s")
            
            # Display or save results
            if output:
                _save_scrape_result(result, output, formats[0])
                console.print(f"[green]✓[/green] Saved to {output}")
            else:
                _display_scrape_result(result, formats[0])
        else:
            console.print(f"[red]✗[/red] Scraping failed: {result.error}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("url")
@click.option("--max-pages", type=int, default=100, help="Maximum pages to crawl")
@click.option("--max-depth", type=int, default=3, help="Maximum crawl depth")
@click.option("--include", multiple=True, help="URL patterns to include")
@click.option("--exclude", multiple=True, help="URL patterns to exclude")
@click.option("--output", "-o", help="Output directory for results")
@click.option("--format", "-f", type=click.Choice(["markdown", "html"]), default="markdown")
@click.pass_context
def crawl(
    ctx,
    url: str,
    max_pages: int,
    max_depth: int,
    include: tuple,
    exclude: tuple,
    output: Optional[str],
    format: str,
):
    """Crawl a website starting from the given URL."""
    app = ctx.obj["app"]
    
    try:
        # Start crawl
        console.print(f"[blue]Starting crawl of {url}...[/blue]")
        console.print(f"  Max pages: {max_pages}")
        console.print(f"  Max depth: {max_depth}")
        
        result = app.crawl_url(
            url,
            max_pages=max_pages,
            max_depth=max_depth,
            include_patterns=list(include) if include else None,
            exclude_patterns=list(exclude) if exclude else None,
            formats=[OutputFormat(format)],
        )
        
        if result.status == "completed":
            console.print(f"\n[green]✓[/green] Crawl completed successfully!")
            console.print(f"  Pages crawled: {result.pages_crawled}")
            console.print(f"  Pages failed: {result.pages_failed}")
            console.print(f"  Duration: {result.duration:.2f}s")
            
            # Save results if output specified
            if output:
                output_dir = Path(output)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                for i, page in enumerate(result.pages):
                    if page.success and format in page.content:
                        filename = f"page_{i+1}.{format[:3]}"
                        filepath = output_dir / filename
                        filepath.write_text(page.content[format])
                
                console.print(f"\n[green]✓[/green] Results saved to {output_dir}")
        else:
            console.print(f"\n[red]✗[/red] Crawl failed: {result.error}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("url")
@click.option("--search", "-s", help="Filter URLs by search term")
@click.option("--limit", type=int, default=5000, help="Maximum URLs to return")
@click.option("--include-subdomains", is_flag=True, help="Include subdomain URLs")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def map(
    ctx,
    url: str,
    search: Optional[str],
    limit: int,
    include_subdomains: bool,
    output: Optional[str],
):
    """Map all URLs from a website."""
    app = ctx.obj["app"]
    
    try:
        # Map website
        with console.status(f"Mapping {url}..."):
            result = app.map_url(
                url,
                search=search,
                limit=limit,
                include_subdomains=include_subdomains,
            )
        
        if result.success:
            console.print(f"\n[green]✓[/green] Mapping completed in {result.duration:.2f}s")
            console.print(f"  URLs found: {result.total_urls}")
            console.print(f"  Sitemap used: {'Yes' if result.sitemap_found else 'No'}")
            
            # Save or display results
            if output:
                Path(output).write_text("\n".join(result.urls))
                console.print(f"\n[green]✓[/green] URLs saved to {output}")
            else:
                # Display first 10 URLs
                console.print("\n[bold]First 10 URLs:[/bold]")
                for url in result.urls[:10]:
                    console.print(f"  • {url}")
                
                if len(result.urls) > 10:
                    console.print(f"\n  ... and {len(result.urls) - 10} more")
        else:
            console.print(f"[red]✗[/red] Mapping failed")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option(
    "--engine", "-e",
    type=click.Choice(["google", "bing", "duckduckgo"]),
    default="google",
    help="Search engine to use"
)
@click.option("--num-results", "-n", type=int, default=10, help="Number of results")
@click.option("--scrape", is_flag=True, help="Scrape content from results")
@click.option("--format", "-f", type=click.Choice(["markdown", "html", "text"]), default="markdown")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def search(
    ctx,
    query: str,
    engine: str,
    num_results: int,
    scrape: bool,
    format: str,
    output: Optional[str],
):
    """Search the web and optionally scrape results."""
    app = ctx.obj["app"]
    
    try:
        # Perform search
        console.print(f"[blue]Searching for: {query}[/blue]")
        
        result = app.search(
            query,
            engine=SearchEngine(engine),
            num_results=num_results,
            scrape_results=scrape,
            formats=[OutputFormat(format)] if scrape else None,
        )
        
        if result.success:
            console.print(f"\n[green]✓[/green] Found {result.total_results} results\n")
            
            # Create results table
            table = Table(title=f"Search Results - {query}")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Title", style="magenta")
            table.add_column("URL", style="blue")
            if not scrape:
                table.add_column("Snippet", style="white")
            
            for item in result.results:
                row = [str(item.position), item.title, item.url]
                if not scrape:
                    row.append(item.snippet[:100] + "..." if len(item.snippet) > 100 else item.snippet)
                table.add_row(*row)
            
            console.print(table)
            
            # Save results if output specified
            if output:
                _save_search_results(result, output, format if scrape else None)
                console.print(f"\n[green]✓[/green] Results saved to {output}")
        else:
            console.print(f"[red]✗[/red] Search failed")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def setup():
    """Interactive setup wizard for RapidCrawl."""
    console.print(Panel.fit("RapidCrawl Setup Wizard", style="bold blue"))
    
    # Check for existing .env file
    env_path = Path(".env")
    if env_path.exists():
        if not click.confirm("\n.env file already exists. Overwrite?"):
            return
    
    console.print("\nLet's configure RapidCrawl:\n")
    
    # API Key
    api_key = click.prompt("API Key (leave empty for self-hosted mode)", default="", hide_input=True)
    
    # Base URL
    base_url = click.prompt(
        "API Base URL",
        default="https://api.rapidcrawl.io/v1",
        show_default=True
    )
    
    # Timeout
    timeout = click.prompt("Request timeout (seconds)", type=int, default=30, show_default=True)
    
    # Create .env file
    env_content = f"""# RapidCrawl Configuration
RAPIDCRAWL_API_KEY={api_key}
RAPIDCRAWL_BASE_URL={base_url}
RAPIDCRAWL_TIMEOUT={timeout}
"""
    
    env_path.write_text(env_content)
    console.print("\n[green]✓[/green] Configuration saved to .env file")
    
    # Test configuration
    if click.confirm("\nTest configuration?"):
        try:
            app = RapidCrawlApp(api_key=api_key or None, base_url=base_url)
            console.print("[green]✓[/green] Configuration is valid!")
        except Exception as e:
            console.print(f"[red]✗[/red] Configuration test failed: {e}")


def _display_scrape_result(result, format: OutputFormat):
    """Display scrape result in console."""
    if result.title:
        console.print(f"\n[bold]Title:[/bold] {result.title}")
    
    if result.description:
        console.print(f"[bold]Description:[/bold] {result.description}")
    
    if result.content:
        console.print(f"\n[bold]Content ({format.value}):[/bold]\n")
        
        content = result.content.get(format.value, "")
        if format == OutputFormat.MARKDOWN:
            # Use syntax highlighting for markdown
            syntax = Syntax(content[:1000], "markdown", theme="monokai", line_numbers=False)
            console.print(syntax)
            if len(content) > 1000:
                console.print("\n... (truncated)")
        else:
            console.print(content[:1000])
            if len(content) > 1000:
                console.print("\n... (truncated)")
    
    if result.structured_data:
        console.print(f"\n[bold]Structured Data:[/bold]")
        console.print(json.dumps(result.structured_data, indent=2))


def _save_scrape_result(result, output_path: str, format: OutputFormat):
    """Save scrape result to file."""
    output = Path(output_path)
    
    if format == OutputFormat.SCREENSHOT and result.content.get("screenshot"):
        # Save screenshot as image
        import base64
        img_data = base64.b64decode(result.content["screenshot"])
        output.write_bytes(img_data)
    else:
        # Save text content
        content = result.content.get(format.value, "")
        output.write_text(content)


def _save_search_results(result, output_path: str, format: Optional[str]):
    """Save search results to file."""
    output = Path(output_path)
    
    if format and any(r.scraped_content for r in result.results):
        # Save scraped content
        output_dir = output if output.is_dir() else output.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, item in enumerate(result.results):
            if item.scraped_content and item.scraped_content.success:
                content = item.scraped_content.content.get(format, "")
                filename = f"result_{i+1}_{item.title[:30]}.{format[:3]}"
                filepath = output_dir / filename
                filepath.write_text(content)
    else:
        # Save as JSON
        data = {
            "query": result.query,
            "engine": result.engine.value,
            "results": [
                {
                    "position": r.position,
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                }
                for r in result.results
            ]
        }
        output.write_text(json.dumps(data, indent=2))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()