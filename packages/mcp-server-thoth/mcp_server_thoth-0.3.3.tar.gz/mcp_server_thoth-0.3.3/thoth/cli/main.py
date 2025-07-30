"""CLI commands for Thoth."""

import asyncio
from pathlib import Path
from typing import List
import os

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from ..config.settings import ConfigManager
from ..indexer import Indexer
from ..storage.database import Database

console = Console()
config_manager = ConfigManager()


@click.group()
def cli():
    """Thoth - Codebase memory and visualization MCP server."""
    pass


@cli.command()
@click.option('--skip-model', is_flag=True, help='Skip downloading the embedding model')
@click.option('--model-cache-dir', type=click.Path(), help='Directory to cache the model weights')
def init(skip_model: bool, model_cache_dir: str):
    """Initialize Thoth and download required models."""
    console.print("[bold cyan]Initializing Thoth...[/bold cyan]\n")
    
    async def run():
        # Step 1: Initialize database
        with console.status("Setting up database..."):
            try:
                db = Database()
                await db.init_db()
                console.print("[green]✓[/green] Database initialized")
                await db.close()
            except Exception as e:
                console.print(f"[red]✗[/red] Database initialization failed: {e}")
                return False
        
        # Step 2: Create necessary directories
        dirs_to_create = [
            Path.home() / ".thoth",
            Path.home() / ".thoth" / "logs",
            Path.home() / ".thoth" / "cache",
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created directories")
        
        # Step 3: Download embedding model if not skipped
        if not skip_model:
            console.print("\n[bold]Downloading embedding model...[/bold]")
            console.print("[dim]This is a one-time download (~460MB)[/dim]\n")
            
            try:
                # Import here to avoid loading model during other commands
                from ..embeddings.lazy_embedder import LazyEmbedder
                
                # Set cache directory if provided
                if model_cache_dir:
                    os.environ['HF_HOME'] = model_cache_dir
                    console.print(f"[dim]Using model cache directory: {model_cache_dir}[/dim]")
                
                # Pre-download the model by initializing vLLM
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Downloading model weights...", total=100)
                    
                    # Create embedder which will download the model
                    embedder = LazyEmbedder(use_vllm=True)
                    
                    # Force initialization by encoding a test string
                    progress.update(task, advance=50, description="Loading model...")
                    test_embedding = embedder.encode("test")
                    
                    progress.update(task, advance=50, description="Model ready!")
                    
                console.print("[green]✓[/green] Embedding model downloaded and verified")
                
            except Exception as e:
                console.print(f"[red]✗[/red] Model download failed: {e}")
                console.print("[yellow]You can retry with 'thoth init' or skip with 'thoth init --skip-model'[/yellow]")
                return False
        else:
            console.print("[yellow]⚠[/yellow] Skipped model download")
        
        # Step 4: Verify installation
        console.print("\n[bold]Verifying installation...[/bold]")
        
        # Check if we can import all required modules
        try:
            from ..mcp import server
            from ..development_memory.tracker import DevelopmentTracker
            console.print("[green]✓[/green] All modules loaded successfully")
        except Exception as e:
            console.print(f"[red]✗[/red] Module verification failed: {e}")
            return False
        
        # Step 5: Show next steps
        console.print("\n[bold green]✨ Thoth initialized successfully![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Index a repository: [cyan]thoth-cli index <name> <path>[/cyan]")
        console.print("2. Add to Claude: [cyan]claude mcp add thoth -s user -- uvx --python 3.12 mcp-server-thoth[/cyan]")
        console.print("\n[dim]For more help: thoth-cli --help[/dim]")
        
        return True
    
    success = asyncio.run(run())
    if not success:
        console.print("\n[red]Initialization failed. Please check the errors above.[/red]")
        exit(1)


@cli.command()
@click.argument('name')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--tags', '-t', multiple=True, help='Tags for the repository')
@click.option('--related-to', '-r', multiple=True, help='Related repository names')
def index(name: str, path: str, language: str, tags: tuple, related_to: tuple):
    """Index a repository."""
    console.print(f"[bold blue]Indexing repository: {name} at {path}[/bold blue]")
    
    # Save to config
    tags_list = list(tags) if tags else []
    related_list = list(related_to) if related_to else []
    config_manager.add_repository(name, path, language, tags_list, related_list)
    
    async def run():
        db = Database()
        await db.init_db()
        
        indexer = Indexer(db, config_manager)
        
        with console.status(f"[bold blue]Indexing repository '{name}'...[/bold blue]") as status:
            try:
                await indexer.index_repository(name, path, language)
                
                # Get final counts
                async with db.get_session() as session:
                    from sqlalchemy import select, func
                    from ..storage.models import File, Symbol, Repository
                    
                    # Get repository
                    repo_result = await session.execute(
                        select(Repository).where(Repository.name == name)
                    )
                    repo = repo_result.scalar_one_or_none()
                    
                    if repo:
                        # Count files
                        file_count = await session.execute(
                            select(func.count(File.id)).where(File.repository_id == repo.id)
                        )
                        files = file_count.scalar() or 0
                        
                        # Count symbols
                        symbol_count = await session.execute(
                            select(func.count(Symbol.id)).where(Symbol.repository_id == repo.id)
                        )
                        symbols = symbol_count.scalar() or 0
                        
                        console.print(f"\n[green]✓[/green] Successfully indexed repository '[bold cyan]{name}[/bold cyan]'")
                        console.print(f"  [dim]→ {files} files, {symbols} symbols indexed[/dim]")
                    else:
                        console.print(f"\n[green]✓[/green] Repository configuration saved: '[bold cyan]{name}[/bold cyan]'")
                
            except Exception as e:
                console.print(f"\n[red]✗[/red] Error indexing repository: {e}")
                import traceback
                traceback.print_exc()
            finally:
                await db.close()
    
    asyncio.run(run())


@cli.command(name='list')
def list_repos():
    """List indexed repositories."""
    async def run():
        db = Database()
        await db.init_db()
        
        async with db.get_session() as session:
            from sqlalchemy import select
            from ..storage.models import Repository
            
            result = await session.execute(select(Repository))
            repos = result.scalars().all()
            
            if not repos:
                console.print("No repositories indexed yet.")
                return
            
            table = Table(title="Indexed Repositories")
            table.add_column("Name", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Language")
            table.add_column("Last Indexed")
            
            from datetime import datetime
            import pytz
            
            # Get local timezone
            local_tz = pytz.timezone('UTC')
            try:
                import tzlocal
                local_tz = tzlocal.get_localzone()
            except:
                pass
            
            for repo in repos:
                if repo.last_indexed:
                    # Convert UTC to local time
                    utc_time = repo.last_indexed.replace(tzinfo=pytz.UTC)
                    local_time = utc_time.astimezone(local_tz)
                    last_indexed = local_time.strftime("%Y-%m-%d %H:%M %Z")
                else:
                    last_indexed = "Never"
                table.add_row(repo.name, repo.path, repo.language or "N/A", last_indexed)
            
            console.print(table)
        
        await db.close()
    
    asyncio.run(run())


@cli.command()
def server():
    """Start the MCP server."""
    from ..mcp.server import main as server_main
    
    console.print("[bold]Starting Thoth MCP server...[/bold]")
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")


@cli.command()
@click.argument('query')
@click.option('--repo', '-r', multiple=True, help='Repository to search')
def search(query: str, repo: tuple):
    """Search for symbols."""
    async def run():
        db = Database()
        await db.init_db()
        
        async with db.get_session() as session:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from ..storage.models import Symbol, Repository
            
            q = select(Symbol).where(Symbol.name.like(f"%{query}%"))
            
            if repo:
                q = q.join(Repository).where(Repository.name.in_(repo))
            
            q = q.options(
                selectinload(Symbol.file),
                selectinload(Symbol.repository)
            ).limit(20)
            
            result = await session.execute(q)
            symbols = result.scalars().all()
            
            if not symbols:
                console.print(f"No symbols found matching '{query}'")
                return
            
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Symbol", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Location", style="green")
            
            for sym in symbols:
                location = f"{sym.repository.name}/{sym.file.path}:{sym.line}"
                table.add_row(sym.name, sym.type, location)
            
            console.print(table)
        
        await db.close()
    
    asyncio.run(run())


@cli.command()
def config():
    """Show configuration."""
    config = config_manager.load()
    
    console.print("[bold cyan]Thoth Configuration[/bold cyan]")
    console.print(f"Config file: {config_manager.config_path}")
    
    if not config.repositories:
        console.print("\nNo repositories configured yet.")
        return
    
    table = Table(title="Configured Repositories")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Language")
    table.add_column("Tags")
    table.add_column("Related To")
    
    for name, repo in config.repositories.items():
        tags = ", ".join(repo.tags) if repo.tags else ""
        related = ", ".join(repo.related_to) if repo.related_to else ""
        table.add_row(name, repo.path, repo.language, tags, related)
    
    console.print(table)


async def index_repos_for_init(repo_paths: List[str]) -> None:
    """Index repositories during initialization."""
    db = Database()
    await db.init_db()
    
    indexer = Indexer(db, config_manager)
    
    for path in repo_paths:
        repo_path = Path(path).resolve()
        if not repo_path.exists():
            console.print(f"[red]Path does not exist: {path}[/red]")
            continue
            
        repo_name = repo_path.name
        console.print(f"[cyan]Indexing {repo_name}...[/cyan]")
        
        try:
            # Auto-detect relationships based on common patterns
            related = []
            if 'client' in repo_name:
                # Look for server repo
                server_name = repo_name.replace('-client', '').replace('_client', '')
                related.append(server_name)
            elif 'server' in repo_name or not 'client' in repo_name:
                # Look for client repo
                related.extend([f"{repo_name}-client", f"{repo_name}_client"])
            
            # Save to config
            tags = []
            if 'client' in repo_name:
                tags = ['client', 'frontend']
            elif 'server' in repo_name:
                tags = ['server', 'backend']
                
            config_manager.add_repository(repo_name, str(repo_path), 'python', tags, related)
            
            # Index the repository
            await indexer.index_repository(repo_name, str(repo_path), 'python')
            console.print(f"[green]✓[/green] Indexed {repo_name}")
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error indexing {repo_name}: {e}")
    
    await db.close()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()