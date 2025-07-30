"""CLI commands for Thoth."""

import asyncio
from pathlib import Path
from typing import List
import os
import subprocess
import time
import socket
import signal
import sys

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from ..config.settings import ConfigManager
from ..indexer import Indexer
from ..storage.database import Database

console = Console()
config_manager = ConfigManager()


def is_port_open(port: int) -> bool:
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


def wait_for_service(port: int, service_name: str, timeout: int = 30) -> bool:
    """Wait for a service to be available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(port):
            return True
        time.sleep(1)
    return False


def test_tei_service(port: int) -> bool:
    """Test if TEI service is working correctly."""
    try:
        import httpx
        response = httpx.post(
            f"http://localhost:{port}/embed",
            json={"inputs": "test"},
            timeout=5.0
        )
        return response.status_code == 200 and len(response.json()) > 0
    except:
        return False


def test_chromadb_service(port: int) -> bool:
    """Test if ChromaDB service is working correctly."""
    try:
        import httpx
        # Try v2 API first (newer ChromaDB versions)
        response = httpx.get(f"http://localhost:{port}/api/v2/heartbeat", timeout=5.0)
        if response.status_code == 200:
            return True
        # Fallback to v1 API for older versions
        response = httpx.get(f"http://localhost:{port}/api/v1/heartbeat", timeout=5.0)
        return response.status_code == 200
    except:
        return False


def check_docker() -> bool:
    """Check if Docker is available."""
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@click.group()
def cli():
    """Thoth - Codebase memory and visualization MCP server."""
    pass


@cli.command()
@click.option('--start-services/--no-start-services', default=True, help='Start external services (TEI, ChromaDB)')
@click.option('--tei-port', default=8765, help='Port for Text Embeddings Inference server')
@click.option('--chromadb-port', default=8000, help='Port for ChromaDB server')
def init(start_services: bool, tei_port: int, chromadb_port: int):
    """Initialize Thoth database, directories, and external services."""
    console.print("[bold cyan]Initializing Thoth...[/bold cyan]\n")
    
    async def run():
        # Import os here to ensure it's available in this scope
        import os
        
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
        
        # Step 3: Start external services if requested
        if start_services:
            console.print("\n[bold]Starting external services...[/bold]")
            
            # Check Docker availability
            if not check_docker():
                console.print("[yellow]⚠[/yellow] Docker not found. External services require Docker.")
                console.print("  Install Docker from: https://docs.docker.com/get-docker/")
                console.print("  Or run with --no-start-services to skip")
                return False
            
            # Start TEI server
            if is_port_open(tei_port):
                console.print(f"[green]✓[/green] TEI server already running on port {tei_port}")
            else:
                console.print(f"Starting Text Embeddings Inference server on port {tei_port}...")
                tei_script = Path(__file__).parent.parent.parent / "scripts" / "run_tei_server.sh"
                if tei_script.exists():
                    # Start TEI in background
                    subprocess.Popen([str(tei_script)], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    
                    # Wait for service to be ready
                    if wait_for_service(tei_port, "TEI", timeout=60):
                        # Test if it's actually working
                        with console.status("Testing TEI embeddings..."):
                            if test_tei_service(tei_port):
                                console.print(f"[green]✓[/green] TEI server started and working on port {tei_port}")
                            else:
                                console.print(f"[yellow]⚠[/yellow] TEI server started but embeddings not working")
                                console.print("  The server may still be loading the model. This is normal on first run.")
                    else:
                        console.print(f"[red]✗[/red] TEI server failed to start")
                        return False
                else:
                    console.print(f"[yellow]⚠[/yellow] TEI startup script not found at {tei_script}")
            
            # ChromaDB server setup (required for vector storage)
            if is_port_open(chromadb_port):
                if test_chromadb_service(chromadb_port):
                    console.print(f"[green]✓[/green] ChromaDB server already running on port {chromadb_port}")
                else:
                    console.print(f"[red]✗[/red] Port {chromadb_port} is in use but not ChromaDB")
                    return False
            else:
                console.print(f"Starting ChromaDB server on port {chromadb_port}...")
                chromadb_script = Path(__file__).parent.parent.parent / "scripts" / "run_chromadb_server.sh"
                if chromadb_script.exists():
                    # Start ChromaDB in background
                    subprocess.Popen([str(chromadb_script)], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    
                    # Wait for service to be ready
                    if wait_for_service(chromadb_port, "ChromaDB", timeout=30):
                        if test_chromadb_service(chromadb_port):
                            console.print(f"[green]✓[/green] ChromaDB server started on port {chromadb_port}")
                        else:
                            console.print(f"[red]✗[/red] ChromaDB server started but not responding correctly")
                            return False
                    else:
                        console.print(f"[red]✗[/red] ChromaDB server failed to start")
                        console.print("  Run manually: [cyan]./scripts/run_chromadb_server.sh[/cyan]")
                        return False
                else:
                    console.print(f"[yellow]⚠[/yellow] ChromaDB startup script not found at {chromadb_script}")
                    console.print("  Please run manually: [cyan]docker run -p 8000:8000 chromadb/chroma[/cyan]")
                    return False
        
        # Step 4: Create environment file
        env_file = Path.home() / ".thoth" / "env"
        with open(env_file, 'w') as f:
            f.write(f"# Thoth environment variables\n")
            f.write(f"export THOTH_EMBEDDING_SERVER_URL=http://localhost:{tei_port}\n")
            # Always include ChromaDB URL when services are started
            if start_services:
                f.write(f"export THOTH_CHROMADB_SERVER_URL=http://localhost:{chromadb_port}\n")
        console.print(f"[green]✓[/green] Created environment file: {env_file}")
        
        # Step 5: Verify installation
        console.print("\n[bold]Verifying installation...[/bold]")
        
        # Check if we can import all required modules
        try:
            from ..mcp import server
            from ..development_memory.tracker import DevelopmentTracker
            console.print("[green]✓[/green] All modules loaded successfully")
        except Exception as e:
            console.print(f"[red]✗[/red] Module verification failed: {e}")
            return False
        
        # Test storage initialization with external services
        if start_services and is_port_open(tei_port):
            try:
                with console.status("Testing storage initialization..."):
                    from ..storage.backend import ThothStorage
                    # Set env vars for this test
                    os.environ["THOTH_EMBEDDING_SERVER_URL"] = f"http://localhost:{tei_port}"
                    if is_port_open(chromadb_port) and test_chromadb_service(chromadb_port):
                        os.environ["THOTH_CHROMADB_SERVER_URL"] = f"http://localhost:{chromadb_port}"
                    
                    storage = ThothStorage(
                        embedding_server_url=f"http://localhost:{tei_port}",
                        chromadb_server_url=f"http://localhost:{chromadb_port}",
                        use_vllm=True
                    )
                    await storage.initialize()
                    await storage.close()
                console.print("[green]✓[/green] Storage initialization successful")
                console.print(f"  MCP server will start in <1 second with external services")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Storage initialization test failed: {e}")
                console.print("  This may be normal if services are still starting up")
        
        # Step 6: Show next steps
        console.print("\n[bold green]✨ Thoth initialized successfully![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Source environment: [cyan]source {env_file}[/cyan]")
        console.print("2. Index a repository: [cyan]thoth-cli index <name> <path>[/cyan]")
        console.print("3. Add to Claude: [cyan]claude mcp add thoth -s user -- uvx --python 3.12 mcp-server-thoth[/cyan]")
        if start_services:
            console.print("\n[bold]Service URLs:[/bold]")
            console.print(f"  TEI server: http://localhost:{tei_port}")
            console.print(f"  ChromaDB: http://localhost:{chromadb_port} (if using server mode)")
        console.print("\n[dim]For more help: thoth-cli --help[/dim]")
        
        return True
    
    success = asyncio.run(run())
    if not success:
        console.print("\n[red]Initialization failed. Please check the errors above.[/red]")
        exit(1)


@cli.command()
def status():
    """Check status of Thoth services."""
    console.print("[bold cyan]Thoth Service Status[/bold cyan]\n")
    
    # Check database
    db_path = Path.home() / ".thoth" / "index.db"
    if db_path.exists():
        console.print(f"[green]✓[/green] Database exists: {db_path}")
        console.print(f"  Size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        console.print(f"[red]✗[/red] Database not found")
    
    # Check TEI server
    tei_port = 8765
    if is_port_open(tei_port):
        console.print(f"[green]✓[/green] TEI server running on port {tei_port}")
        # Test embedding
        import httpx
        try:
            response = httpx.post(
                f"http://localhost:{tei_port}/embed",
                json={"inputs": "test"},
                timeout=5.0
            )
            if response.status_code == 200:
                console.print("  Embeddings working correctly")
        except:
            console.print("  [yellow]⚠[/yellow] Could not test embeddings")
    else:
        console.print(f"[yellow]✗[/yellow] TEI server not running on port {tei_port}")
        console.print("  Run: ./scripts/run_tei_server.sh")
    
    # Check ChromaDB
    chromadb_port = 8000
    if is_port_open(chromadb_port):
        console.print(f"[green]✓[/green] ChromaDB server running on port {chromadb_port}")
    else:
        console.print(f"[dim]○[/dim] ChromaDB server not running (using embedded mode)")
    
    # Check environment
    env_file = Path.home() / ".thoth" / "env"
    if env_file.exists():
        console.print(f"\n[bold]Environment file:[/bold] {env_file}")
        console.print("  Run: [cyan]source ~/.thoth/env[/cyan] to load environment")
    
    # Show indexed repositories
    try:
        repos = config_manager.get_all_repositories()
        if repos:
            console.print(f"\n[bold]Indexed repositories:[/bold]")
            for repo in repos:
                console.print(f"  • {repo['name']} at {repo['path']}")
        else:
            console.print("\n[dim]No repositories indexed yet[/dim]")
    except:
        pass


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