"""MCP server for codebase memory and visualization."""

import asyncio
import os

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..development_memory.session_hooks import SessionHooks
from ..development_memory.tracker import DevelopmentTracker
from ..storage.backend import ThothStorage
from ..storage.database import Database
from ..storage.models import Call, File, Import, Repository, Symbol
from ..visualizations.mermaid import generate_module_diagram as create_module_diagram
from ..visualizations.mermaid import generate_system_architecture_diagram

# Create a server instance
server = Server("thoth")

# Global instances
db: Database | None = None
storage: ThothStorage | None = None
dev_tracker: DevelopmentTracker | None = None
session_hooks: SessionHooks | None = None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="find_definition",
            description="Search the codebase to locate where a symbol (function, class, method) is defined",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Symbol name to find"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="get_file_structure",
            description="Analyze a file to extract its structure (functions, classes, imports)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path relative to repository"},
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["file_path", "repo"]
            }
        ),
        types.Tool(
            name="search_symbols",
            description="Search the codebase for symbols using partial name matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "type_filter": {
                        "type": "string",
                        "enum": ["function", "class", "method"],
                        "description": "Filter by symbol type (optional)"
                    },
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_callers",
            description="Search the codebase to find all places where a function or method is called",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Function/method name"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="generate_module_diagram",
            description="Create a Mermaid diagram showing module dependencies within a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["repo"]
            }
        ),
        types.Tool(
            name="get_repositories",
            description="Retrieve a list of all indexed repositories in the codebase memory",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="generate_system_architecture",
            description="Create a comprehensive system architecture diagram showing all repositories and their relationships",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="trace_api_flow",
            description="Trace through the codebase to map the flow from a client API call to its server handler",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "API endpoint path or WebSocket message name"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="index_repository",
            description="Analyze and index a repository to add it to the persistent codebase memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Repository name (used as identifier)"},
                    "path": {"type": "string", "description": "Absolute path to the repository directory"},
                    "language": {"type": "string", "description": "Programming language (default: python)", "default": "python"}
                },
                "required": ["name", "path"]
            }
        ),
        types.Tool(
            name="search_semantic",
            description="Search the codebase for symbols using natural language queries and semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"},
                    "repo": {"type": "string", "description": "Filter by repository name (optional)"},
                    "symbol_type": {
                        "type": "string",
                        "enum": ["function", "class", "method"],
                        "description": "Filter by symbol type (optional)"
                    },
                    "limit": {"type": "integer", "description": "Maximum results (default: 10)", "default": 10}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="start_dev_session",
            description="Initialize a development session to track coding attempts and learn from successes and failures",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {"type": "string", "description": "Repository name"},
                    "task": {"type": "string", "description": "Description of what you're trying to achieve"}
                },
                "required": ["repository", "task"]
            }
        ),
        types.Tool(
            name="track_attempt",
            description="Record a development attempt (edit, test, refactor) to build knowledge of what works",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["edit", "create", "delete", "refactor", "test"],
                        "description": "Type of action"
                    },
                    "target_file": {"type": "string", "description": "File being modified (optional)"},
                    "approach": {"type": "string", "description": "Description of approach"},
                    "success": {"type": "boolean", "description": "Whether attempt succeeded"},
                    "error_message": {"type": "string", "description": "Error message if failed"}
                },
                "required": ["action_type", "approach", "success"]
            }
        ),
        types.Tool(
            name="check_approach",
            description="Query the development memory to check if an approach has been tried before and its outcome",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["edit", "create", "delete", "refactor", "test"],
                        "description": "Type of action"
                    },
                    "target_file": {"type": "string", "description": "File pattern (optional)"},
                    "approach": {"type": "string", "description": "Description of approach"}
                },
                "required": ["action_type"]
            }
        ),
        types.Tool(
            name="analyze_failure",
            description="Analyze past failures and successful solutions to extract actionable insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Problem or error description"},
                    "repository": {"type": "string", "description": "Repository name (optional)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="analyze_patterns",
            description="Analyze development patterns to identify common failure modes and suggest improvements",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {"type": "string", "description": "Repository name (optional)"},
                    "days": {"type": "integer", "description": "Time window in days (default: 30)", "default": 30}
                }
            }
        )
    ]


def create_error_response(message: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Create a consistent error response."""
    return [types.TextContent(type="text", text=message)]


def create_success_response(message: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Create a consistent success response."""
    return [types.TextContent(type="text", text=message)]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    global db, storage, dev_tracker, session_hooks
    if db is None:
        db = Database()
        await db.init_db()
    if storage is None:
        # Get server URLs from environment
        embedding_server_url = os.getenv("THOTH_EMBEDDING_SERVER_URL")
        chromadb_server_url = os.getenv("THOTH_CHROMADB_SERVER_URL")
        
        storage = ThothStorage(
            embedding_server_url=embedding_server_url,
            chromadb_server_url=chromadb_server_url,
            use_vllm=bool(embedding_server_url)  # Use vLLM if server URL is provided
        )
        await storage.initialize()
    if dev_tracker is None:
        dev_tracker = DevelopmentTracker(db)
    if session_hooks is None:
        session_hooks = SessionHooks()
    
    if name == "find_definition":
        return await find_definition(arguments)
    elif name == "get_file_structure":
        return await get_file_structure(arguments)
    elif name == "search_symbols":
        return await search_symbols(arguments)
    elif name == "get_callers":
        return await get_callers(arguments)
    elif name == "generate_module_diagram":
        return await generate_module_diagram(arguments)
    elif name == "get_repositories":
        return await get_repositories(arguments)
    elif name == "generate_system_architecture":
        return await generate_system_architecture(arguments)
    elif name == "trace_api_flow":
        return await trace_api_flow(arguments)
    elif name == "index_repository":
        return await index_repository(arguments)
    elif name == "search_semantic":
        return await search_semantic(arguments)
    elif name == "start_dev_session":
        return await start_dev_session(arguments)
    elif name == "track_attempt":
        return await track_attempt(arguments)
    elif name == "check_approach":
        return await check_approach(arguments)
    elif name == "analyze_failure":
        return await analyze_failure(arguments)
    elif name == "analyze_patterns":
        return await analyze_patterns(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def find_definition(args: dict) -> list[types.TextContent]:
    """Find symbol definition."""
    name = args["name"]
    repos = args.get("repos", [])
    
    async with db.get_session() as session:
        query = select(Symbol).where(Symbol.name == name)
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        query = query.options(
            selectinload(Symbol.file),
            selectinload(Symbol.repository)
        )
        
        results = await session.execute(query)
        symbols = results.scalars().all()
        
        if not symbols:
            return create_error_response(f"No definition found for '{name}'\n\nSuggestions:\n- Check if the symbol name is spelled correctly\n- Use 'search_symbols' for partial name matching\n- Ensure the repository containing this symbol has been indexed")
        
        lines = []
        for sym in symbols:
            repo_name = sym.repository.name
            file_path = sym.file.path
            lines.append(f"{repo_name}/{file_path}:{sym.line} - {sym.type} {sym.name}")
            if sym.docstring:
                lines.append(f"  Docstring: {sym.docstring[:100]}...")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def get_file_structure(args: dict) -> list[types.TextContent]:
    """Get file structure."""
    file_path = args["file_path"]
    repo_name = args["repo"]
    
    async with db.get_session() as session:
        # Get file
        result = await session.execute(
            select(File)
            .join(Repository)
            .where(
                Repository.name == repo_name,
                File.path == file_path
            )
            .options(
                selectinload(File.symbols),
                selectinload(File.imports)
            )
        )
        file = result.scalar_one_or_none()
        
        if not file:
            return create_error_response(f"File not found: {repo_name}/{file_path}")
        
        lines = [f"File: {repo_name}/{file_path}"]
        
        # List imports
        if file.imports:
            lines.append("\nImports:")
            for imp in file.imports:
                import_str = f"  - {imp.module}"
                if imp.name:
                    import_str += f".{imp.name}"
                if imp.alias:
                    import_str += f" as {imp.alias}"
                lines.append(import_str)
        
        # List symbols
        if file.symbols:
            lines.append("\nSymbols:")
            # Group by type
            classes = [s for s in file.symbols if s.type == 'class']
            functions = [s for s in file.symbols if s.type == 'function']
            methods = [s for s in file.symbols if s.type == 'method']
            
            if classes:
                lines.append("  Classes:")
                for cls in classes:
                    lines.append(f"    - {cls.name} (line {cls.line})")
                    # List methods under class
                    class_methods = [m for m in methods if m.parent_id == cls.id]
                    for method in class_methods:
                        lines.append(f"      - {method.name} (line {method.line})")
            
            if functions:
                lines.append("  Functions:")
                for func in functions:
                    lines.append(f"    - {func.name} (line {func.line})")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def search_symbols(args: dict) -> list[types.TextContent]:
    """Search symbols by name."""
    # Validate required parameters
    if "query" not in args or not args["query"]:
        return create_error_response("Error: 'query' parameter is required and cannot be empty")
    
    query_str = str(args["query"]).strip()
    type_filter = args.get("type_filter")
    repos = args.get("repos", [])
    
    # Validate type_filter if provided
    if type_filter and type_filter not in ["function", "class", "method"]:
        return create_error_response("Error: 'type_filter' must be one of: function, class, method")
    
    async with db.get_session() as session:
        query = select(Symbol).where(Symbol.name.like(f"%{query_str}%"))
        
        if type_filter:
            query = query.where(Symbol.type == type_filter)
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        # Order by name similarity and then by deterministic fields
        query = query.options(
            selectinload(Symbol.file),
            selectinload(Symbol.repository)
        ).order_by(
            Symbol.name,
            Symbol.file_id,
            Symbol.line
        ).limit(50)
        
        results = await session.execute(query)
        symbols = results.scalars().all()
        
        if not symbols:
            return create_error_response(f"No symbols found matching '{query_str}'")
        
        lines = [f"Found {len(symbols)} symbols:"]
        for sym in symbols:
            repo_name = sym.repository.name
            file_path = sym.file.path
            lines.append(f"- {sym.type} {sym.name} in {repo_name}/{file_path}:{sym.line}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def get_callers(args: dict) -> list[types.TextContent]:
    """Find callers of a function."""
    # Validate required parameters
    if "name" not in args or not args["name"]:
        return create_error_response("Error: 'name' parameter is required and cannot be empty")
    
    name = str(args["name"]).strip()
    repos = args.get("repos", [])
    
    async with db.get_session() as session:
        # Find the symbol
        query = select(Symbol).where(Symbol.name == name).options(
            selectinload(Symbol.repository)
        )
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        result = await session.execute(query)
        symbols = result.scalars().all()
        
        if not symbols:
            return create_error_response(f"No symbol found: '{name}'")
        
        lines = []
        
        for symbol in symbols:
            # Find calls to this symbol
            # Order calls deterministically
            result = await session.execute(
                select(Call)
                .where(Call.callee_symbol_id == symbol.id)
                .options(
                    selectinload(Call.file),
                    selectinload(Call.caller)
                )
                .order_by(Call.file_id, Call.line)
            )
            calls = result.scalars().all()
            
            if calls:
                lines.append(f"\nCallers of {symbol.type} '{name}' in {symbol.repository.name}:")
                
                for call in calls:
                    caller_name = call.caller.name if call.caller else "<module>"
                    file_path = call.file.path
                    lines.append(f"  - {caller_name} at {file_path}:{call.line}")
        
        if not lines:
            return create_error_response(f"No callers found for '{name}'")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def generate_module_diagram(args: dict) -> list[types.TextContent]:
    """Generate module dependency diagram."""
    repo_name = args["repo"]
    
    async with db.get_session() as session:
        # Get repository
        result = await session.execute(
            select(Repository).where(Repository.name == repo_name)
        )
        repo = result.scalar_one_or_none()
        
        if not repo:
            return create_error_response(f"Repository not found: {repo_name}")
        
        # Get all imports for the repository
        result = await session.execute(
            select(Import)
            .join(File)
            .where(File.repository_id == repo.id)
            .options(
                selectinload(Import.file).selectinload(File.repository),
                selectinload(Import.resolved_repository)
            )
        )
        imports = result.scalars().all()
        
        # Generate diagram
        diagram = create_module_diagram(imports)
        
        return [types.TextContent(
            type="text",
            text=f"```mermaid\n{diagram}\n```"
        )]


async def get_repositories(args: dict) -> list[types.TextContent]:
    """List all repositories."""
    async with db.get_session() as session:
        # Order by name for deterministic results
        result = await session.execute(
            select(Repository).order_by(Repository.name)
        )
        repos = result.scalars().all()
        
        if not repos:
            return create_error_response("No repositories indexed yet")
        
        lines = ["Indexed repositories:"]
        for repo in repos:
            status = f"(last indexed: {repo.last_indexed})" if repo.last_indexed else "(not indexed)"
            lines.append(f"- {repo.name}: {repo.path} {status}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def generate_system_architecture(args: dict) -> list[types.TextContent]:
    """Generate system architecture diagram."""
    async with db.get_session() as session:
        # Get all repositories
        result = await session.execute(select(Repository))
        repositories = result.scalars().all()
        
        if not repositories:
            return create_error_response("No repositories indexed yet")
        
        # Get all imports with resolved cross-repo dependencies
        result = await session.execute(
            select(Import)
            .where(Import.resolved_repository_id.isnot(None))
            .options(
                selectinload(Import.file).selectinload(File.repository)
            )
        )
        imports = result.scalars().all()
        
        # Generate diagram
        diagram = generate_system_architecture_diagram(repositories, imports)
        
        return [types.TextContent(
            type="text",
            text=f"```mermaid\n{diagram}\n```"
        )]


async def trace_api_flow(args: dict) -> list[types.TextContent]:
    """Trace API flow from client to server."""
    query = args["query"]
    
    async with db.get_session() as session:
        lines = [f"Tracing API flow for: {query}\n"]
        
        # Search for WebSocket send/emit calls in client
        client_calls = await find_websocket_calls(session, query, "slush-client")
        
        if client_calls:
            lines.append("=== Client Side ===")
            for call in client_calls:
                lines.append(f"\nFound in {call['file']}:{call['line']}")
                lines.append(f"Function: {call['function']}")
                lines.append(f"Context: {call['context']}")
        
        # Search for WebSocket handlers in server
        server_handlers = await find_websocket_handlers(session, query, "slush")
        
        if server_handlers:
            lines.append("\n=== Server Side ===")
            for handler in server_handlers:
                lines.append(f"\nHandler in {handler['file']}:{handler['line']}")
                lines.append(f"Function: {handler['function']}")
                
                # Find what this handler calls
                if handler['symbol_id']:
                    calls = await get_function_calls(session, handler['symbol_id'])
                    if calls:
                        lines.append("Calls:")
                        for call in calls:
                            lines.append(f"  - {call}")
        
        # Generate sequence diagram
        if client_calls and server_handlers:
            lines.append("\n=== Sequence Diagram ===")
            lines.append("```mermaid")
            lines.append("sequenceDiagram")
            lines.append("    participant Client")
            lines.append("    participant Server")
            lines.append(f"    Client->>Server: {query}")
            
            for handler in server_handlers:
                lines.append(f"    Note over Server: {handler['function']}")
            
            lines.append("    Server-->>Client: Response")
            lines.append("```")
        
        if not client_calls and not server_handlers:
            lines.append(f"No API flow found for '{query}'")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def find_websocket_calls(session, query: str, repo_name: str) -> list[dict]:
    """Find WebSocket calls in client code."""
    # Search for symbols containing 'send' or 'emit'
    result = await session.execute(
        select(Symbol)
        .join(Repository)
        .where(
            Repository.name == repo_name,
            Symbol.name.in_(['send', 'emit', 'send_message', 'sendMessage'])
        )
        .options(selectinload(Symbol.file))
    )
    symbols = result.scalars().all()
    
    results = []
    for symbol in symbols:
        # Check if this function might send the query message
        # This is a simplified check - in reality we'd parse the function body
        results.append({
            'file': f"{repo_name}/{symbol.file.path}",
            'line': symbol.line,
            'function': symbol.name,
            'context': f"Potential sender of '{query}'",
            'symbol_id': symbol.id
        })
    
    return results


async def find_websocket_handlers(session, query: str, repo_name: str) -> list[dict]:
    """Find WebSocket handlers in server code."""
    # Search for handler functions
    # Look for patterns like 'on_<message>' or 'handle_<message>'
    patterns = [
        f"on_{query}",
        f"handle_{query}",
        query,  # Direct match
        "message_handler",  # Generic handlers
        "websocket_handler"
    ]
    
    result = await session.execute(
        select(Symbol)
        .join(Repository)
        .where(
            Repository.name == repo_name,
            Symbol.name.in_(patterns)
        )
        .options(selectinload(Symbol.file))
    )
    symbols = result.scalars().all()
    
    results = []
    for symbol in symbols:
        results.append({
            'file': f"{repo_name}/{symbol.file.path}",
            'line': symbol.line,
            'function': symbol.name,
            'symbol_id': symbol.id
        })
    
    return results


async def get_function_calls(session, symbol_id: int) -> list[str]:
    """Get functions called by a symbol."""
    result = await session.execute(
        select(Call)
        .where(Call.caller_symbol_id == symbol_id)
        .options(selectinload(Call.callee))
    )
    calls = result.scalars().all()
    
    return [call.callee.name for call in calls if call.callee]


async def index_repository(args: dict) -> list[types.TextContent]:
    """Index a new repository."""
    # Validate required parameters
    if "name" not in args or not args["name"]:
        return create_error_response("Error: 'name' parameter is required and cannot be empty")
    if "path" not in args or not args["path"]:
        return create_error_response("Error: 'path' parameter is required and cannot be empty")
    
    name = str(args["name"]).strip()
    path = str(args["path"]).strip()
    language = str(args.get("language", "python")).strip().lower()
    
    # Validate language
    supported_languages = ["python", "javascript", "typescript", "java", "go", "rust"]
    if language not in supported_languages:
        return create_error_response(f"Error: Unsupported language '{language}'. Supported languages: {', '.join(supported_languages)}")
    
    # Validate path exists
    from pathlib import Path
    repo_path = Path(path)
    if not repo_path.exists():
        return create_error_response(f"Error: Path '{path}' does not exist")
    if not repo_path.is_dir():
        return create_error_response(f"Error: Path '{path}' is not a directory")
    
    # Import here to avoid circular imports
    from ..config.settings import ConfigManager
    from ..indexer import Indexer
    
    try:
        # Create a config manager instance
        config_manager = ConfigManager()
        
        # Add repository to config
        config_manager.add_repository(name, path, language, [], [])
        
        # Create indexer and index the repository
        global storage
        indexer = Indexer(db, config_manager, storage)
        await indexer.index_repository(name, path, language)
        
        return create_success_response(f"Successfully indexed repository '{name}' at path '{path}'")
    except Exception as e:
        error_msg = f"Error indexing repository '{name}': {str(e)}"
        
        # Add helpful context based on error type
        if "ambiguous" in str(e).lower() and "foreign" in str(e).lower():
            error_msg += "\n\nThis appears to be a database schema issue. The indexer may need to be updated."
        elif "timeout" in str(e).lower():
            error_msg += "\n\nSuggestion: The operation timed out. Try running 'thoth-cli init' first to pre-download models."
        elif "permission" in str(e).lower():
            error_msg += "\n\nSuggestion: Check that you have read permissions for the repository path."
        
        return create_error_response(error_msg)


async def search_semantic(args: dict) -> list[types.TextContent]:
    """Semantic search for symbols."""
    # Validate required parameters
    if "query" not in args or not args["query"]:
        return create_error_response("Error: 'query' parameter is required and cannot be empty")
    
    query = str(args["query"]).strip()
    repo = str(args.get("repo", "")).strip() if args.get("repo") else None
    symbol_type = args.get("symbol_type")
    limit = args.get("limit", 10)
    
    # Validate symbol_type if provided
    if symbol_type and symbol_type not in ["function", "class", "method"]:
        return create_error_response("Error: 'symbol_type' must be one of: function, class, method")
    
    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return create_error_response("Error: 'limit' must be an integer between 1 and 100")
    
    global storage
    if storage is None:
        return create_error_response("Storage not initialized. Please wait a moment for the service to start, or run 'thoth-cli init' to pre-download models.")
    
    try:
        # Perform semantic search
        results = await storage.search_semantic(
            query=query,
            repo=repo,
            symbol_type=symbol_type,
            limit=limit
        )
        
        if not results:
            return create_error_response(f"No symbols found matching: '{query}'\n\nSuggestions:\n- Try different keywords or phrases\n- Check if the relevant repositories have been indexed\n- Use more specific technical terms related to your search")
        
        # Format results
        lines = [f"Found {len(results)} symbols matching '{query}':\n"]
        
        for result in results:
            lines.append(f"- {result['type']} {result['name']} (score: {result['score']:.3f})")
            lines.append(f"  Location: {result['repo']}/{result['file_path']}:{result['line']}")
            lines.append(f"  Preview: {result['preview']}")
            lines.append("")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]
        
    except Exception as e:
        error_msg = f"Error performing semantic search: {str(e)}"
        
        # Add context for common errors
        if "timeout" in str(e).lower():
            error_msg += "\n\nThe embedding model is still loading. This can take 30-60 seconds on first use.\nSuggestion: Run 'thoth-cli init' to pre-download the model and avoid timeouts."
        elif "cuda" in str(e).lower() or "gpu" in str(e).lower():
            error_msg += "\n\nGPU-related error detected. The system will fall back to CPU if needed."
        elif "model" in str(e).lower() and "not found" in str(e).lower():
            error_msg += "\n\nThe embedding model needs to be downloaded. Run 'thoth-cli init' to set it up."
        
        return create_error_response(error_msg)


async def start_dev_session(args: dict) -> list[types.TextContent]:
    """Start a development session."""
    # Validate required parameters
    if "repository" not in args or not args["repository"]:
        return create_error_response("Error: 'repository' parameter is required and cannot be empty")
    if "task" not in args or not args["task"]:
        return create_error_response("Error: 'task' parameter is required and cannot be empty")
    
    repository = str(args["repository"]).strip()
    task = str(args["task"]).strip()
    
    global dev_tracker, session_hooks
    if dev_tracker is None:
        return create_error_response("Development tracker not initialized. This feature tracks coding attempts to learn from failures.\n\nTo use development memory:\n1. Ensure Thoth is properly initialized\n2. Start a development session first\n3. Track your attempts as you work")
    
    try:
        # Check if there's an existing session
        existing = session_hooks.get_current_session()
        if existing:
            return create_success_response(f"Resuming existing session {existing['session_id']}\nRepository: {existing['repository']}\nStarted: {existing['timestamp']}")
        
        # Start new session
        session_id = await dev_tracker.start_session(repository, task)
        
        # Save for persistence
        session_hooks.save_current_session(session_id, repository)
        
        return create_success_response(f"Started development session {session_id}\nRepository: {repository}\nTask: {task}")
    except Exception as e:
        return create_error_response(f"Error starting session: {str(e)}")


async def track_attempt(args: dict) -> list[types.TextContent]:
    """Track a development attempt."""
    action_type = args["action_type"]
    approach = args["approach"]
    success = args["success"]
    target_file = args.get("target_file")
    error_message = args.get("error_message")
    
    global dev_tracker
    if dev_tracker is None:
        return create_error_response("Development tracker not initialized")
    
    try:
        # Determine error type from message if failed
        error_type = None
        if not success and error_message:
            if "ImportError" in error_message or "No module named" in error_message:
                error_type = "import_error"
            elif "AttributeError" in error_message:
                error_type = "attribute_error"
            elif "TypeError" in error_message:
                error_type = "type_error"
            elif "SyntaxError" in error_message:
                error_type = "syntax_error"
            elif "test" in error_message.lower():
                error_type = "test_failure"
            else:
                error_type = "runtime_error"
        
        attempt_id = await dev_tracker.track_attempt(
            action_type=action_type,
            target_file=target_file,
            approach_description=approach,
            success=success,
            error_message=error_message,
            error_type=error_type
        )
        
        status = "succeeded" if success else "failed"
        msg = f"Tracked {action_type} attempt #{attempt_id}: {status}"
        if target_file:
            msg += f"\nFile: {target_file}"
        if not success and error_message:
            msg += f"\nError: {error_message[:200]}..."
            
        return create_success_response(msg)
    except Exception as e:
        return create_error_response(f"Error tracking attempt: {str(e)}")


async def check_approach(args: dict) -> list[types.TextContent]:
    """Check if an approach has been tried before."""
    action_type = args["action_type"]
    target_file = args.get("target_file")
    
    global dev_tracker
    if dev_tracker is None:
        return create_error_response("Development tracker not initialized")
    
    try:
        # Find similar attempts
        similar = await dev_tracker.find_similar_attempts(
            action_type=action_type,
            target_file=target_file,
            limit=5
        )
        
        if not similar:
            return create_error_response(f"No similar {action_type} attempts found")
        
        lines = [f"Found {len(similar)} similar {action_type} attempts:\n"]
        
        for attempt in similar:
            lines.append(f"- {attempt['timestamp']} ({attempt['task']})")
            lines.append(f"  Approach: {attempt['approach']}")
            lines.append(f"  Result: {'Success' if attempt['success'] else 'Failed'}")
            if not attempt['success']:
                lines.append(f"  Error: {attempt['error_type']} - {attempt['error_message'][:100]}...")
            lines.append("")
            
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]
    except Exception as e:
        return create_error_response(f"Error checking approach: {str(e)}")


async def analyze_failure(args: dict) -> list[types.TextContent]:
    """Get insights from past failures and solutions."""
    query = args["query"]
    repository = args.get("repository")
    
    global dev_tracker
    if dev_tracker is None:
        return create_error_response("Development tracker not initialized")
    
    try:
        lines = []
        
        # Search for solutions
        solutions = await dev_tracker.search_solutions(
            query=query,
            repository_name=repository
        )
        
        if solutions:
            lines.append(f"=== Found {len(solutions)} relevant solutions ===\n")
            for solution in solutions:
                lines.append(f"Problem: {solution['problem']}")
                lines.append(f"Solution: {solution['solution']}")
                if solution['code_example']:
                    lines.append(f"Example:\n```\n{solution['code_example']}\n```")
                lines.append(f"Success rate: {solution['success_rate']}% (used {solution['times_used']} times)")
                lines.append("")
        
        # Get failure patterns
        patterns = await dev_tracker.get_failure_patterns(
            repository_name=repository,
            min_occurrences=1
        )
        
        # Filter patterns related to query
        relevant_patterns = []
        for pattern in patterns:
            if query.lower() in pattern['description'].lower() or query.lower() in pattern['pattern_type'].lower():
                relevant_patterns.append(pattern)
        
        if relevant_patterns:
            lines.append("=== Common failure patterns ===\n")
            for pattern in relevant_patterns[:5]:
                lines.append(f"- {pattern['pattern_type']}: {pattern['description']}")
                lines.append(f"  Occurred {pattern['occurrences']} times")
                if pattern['suggested_solution']:
                    lines.append(f"  Suggestion: {pattern['suggested_solution']}")
                lines.append("")
        
        if not solutions and not relevant_patterns:
            lines.append(f"No specific insights found for '{query}'")
            lines.append("\nTip: Track more attempts to build up the knowledge base!")
            
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]
    except Exception as e:
        return create_error_response(f"Error learning from failures: {str(e)}")


async def analyze_patterns(args: dict) -> list[types.TextContent]:
    """Analyze failure patterns and get suggestions."""
    repository = args.get("repository")
    days = args.get("days", 30)
    
    global dev_tracker, db
    if dev_tracker is None:
        return create_error_response("Development tracker not initialized")
    
    try:
        # Get repository ID if specified
        repo_id = None
        if repository:
            async with db.get_session() as session:
                result = await session.execute(
                    select(Repository).where(Repository.name == repository)
                )
                repo = result.scalar_one_or_none()
                if repo:
                    repo_id = repo.id
        
        # Analyze patterns
        analysis = await dev_tracker.analyze_failure_patterns(
            repository_id=repo_id,
            time_window_days=days
        )
        
        # Format results
        lines = [f"=== Failure Pattern Analysis ({days} days) ===\n"]
        
        lines.append(f"Total failures: {analysis['total_failures']}")
        
        if analysis['common_error_types']:
            lines.append("\n=== Most Common Error Types ===")
            for error_type, count in analysis['common_error_types']:
                lines.append(f"- {error_type}: {count} occurrences")
        
        if analysis['problematic_files']:
            lines.append("\n=== Most Problematic Files ===")
            for file_path, count in analysis['problematic_files']:
                lines.append(f"- {file_path}: {count} failures")
        
        if analysis['error_clusters']:
            lines.append("\n=== Error Patterns ===")
            for cluster in analysis['error_clusters']:
                lines.append(f"\n- Pattern: {cluster['pattern']}")
                lines.append(f"  Occurrences: {cluster['count']}")
                if cluster['files']:
                    lines.append(f"  Files: {', '.join(cluster['files'][:3])}")
                if cluster['examples']:
                    lines.append(f"  Example: {cluster['examples'][0]}")
        
        if analysis['suggestions']:
            lines.append("\n=== Suggestions ===")
            for suggestion in analysis['suggestions']:
                lines.append(f"- {suggestion}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]
        
    except Exception as e:
        return create_error_response(f"Error analyzing patterns: {str(e)}")


async def main():
    """Run the MCP server."""
    # Don't initialize storage here - do it lazily on first use
    # This prevents timeout during MCP server startup
    
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="thoth",
                server_version="0.3.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())