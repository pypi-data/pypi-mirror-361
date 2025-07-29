# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server implementation for QUADS. It uses the FastMCP framework to expose tools, resources, and prompts to LLM applications like Claude. The project is written in Python 3.12+ and follows modern Python packaging standards.

## Development Commands

### Setup and Environment
```bash
# Initial setup (creates virtual environment and installs dependencies)
make setup

# Activate virtual environment
source .venv/bin/activate  # Unix/MacOS
# or
.venv\Scripts\activate     # Windows
```

### Development Workflow
```bash
# Run with uvx (easiest, no setup required)
uvx --from . quads-mcp

# Run server directly
make run
# or
python -m quads_mcp.server

# Run in development mode with MCP inspector
make dev
# or
mcp dev quads_mcp.server

# Install in Claude Desktop
make install
# or
mcp install quads_mcp.server
```

### Testing and Quality
```bash
# Run tests
make test
# or
pytest

# Format code
make format
# This runs: black quads_mcp && isort quads_mcp

# Type checking
make type-check
# or
mypy quads_mcp

# Clean build artifacts
make clean
```

### Containers
```bash
# Build container image
make container-build

# Run with Podman
make container-run
```

## Architecture

### Core Components

1. **server.py**: Main FastMCP server initialization with lifecycle management
   - Uses `AppContext` dataclass for type-safe application state
   - Implements `app_lifespan` async context manager for startup/shutdown
   - Imports all tools, resources, and prompts via wildcard imports

2. **config.py**: Configuration management system
   - Supports environment variables with `MCP_` prefix
   - Supports JSON config files (via `MCP_CONFIG_FILE` env var)
   - Supports `.env` files (via python-dotenv library)
   - Handles nested configuration with double underscore syntax (`MCP_DATABASE__HOST`)
   - Automatic type conversion for environment variables

3. **tools/**: MCP tool implementations (functions LLMs can execute)
   - Use `@mcp.tool()` decorator
   - Support async operations and context injection
   - Pattern: `async def tool_name(params, ctx: Context) -> return_type`

4. **resources/**: MCP resource implementations (data sources for LLMs)
   - Use `@mcp.resource("uri://pattern")` decorator
   - Support parameterized URIs with `{parameter}` syntax
   - Can access app context via `mcp.get_request_context()`

5. **prompts/**: MCP prompt template implementations
   - Use `@mcp.prompt()` decorator
   - Can return strings or `list[base.Message]` for structured conversations
   - Support parameterized prompt generation

### Key Patterns

- **Context Injection**: Tools can receive `Context` object for logging and progress reporting
- **Async Support**: All tools and resources support async operations
- **Type Safety**: Uses proper type hints and dataclasses
- **Configuration**: Hierarchical config system with environment variable override
- **Error Handling**: Comprehensive error handling in tools with proper logging

### Configuration System

The configuration system supports multiple sources in order of precedence:

1. **Environment variables** (highest priority)
2. **JSON config files** (via `MCP_CONFIG_FILE`)
3. **`.env` files** (lowest priority)

#### Environment Variables
- `MCP_CONFIG_FILE`: Path to JSON config file
- `MCP_*`: Any environment variable with this prefix becomes config
- `MCP_DATABASE__HOST`: Creates nested config `{"database": {"host": "value"}}`

#### .env File Support
Create a `.env` file in the project root:
```bash
# QUADS API Configuration
MCP_QUADS__BASE_URL=https://quads.example.com/api/v3
MCP_QUADS__AUTH_TOKEN=your-auth-token-here
MCP_QUADS__TIMEOUT=30
```

#### JSON Config File
```json
{
  "quads": {
    "base_url": "https://quads.example.com/api/v3",
    "auth_token": "your-auth-token",
    "timeout": 30
  }
}
```

#### QUADS-Specific Configuration
For QUADS integration, configure:
- `MCP_QUADS__BASE_URL`: QUADS API base URL
- `MCP_QUADS__AUTH_TOKEN`: Authentication token
- `MCP_QUADS__TIMEOUT`: Request timeout (optional, defaults to 30s)

## Development Notes

- Python 3.12+ required
- Uses `uv` for dependency management
- Code formatting with `black` and `isort` (88 character line length)
- Type checking with `mypy`
- Testing with `pytest`
- Dependencies: `mcp>=1.0`, `httpx>=0.24.0`, `python-dotenv>=1.0.0`

## Adding New Components

When adding new tools, resources, or prompts:
1. Create the implementation in the appropriate subdirectory
2. Use the correct decorator (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`)
3. Follow the existing patterns for async operations and context usage
4. Import the new module in `server.py` or ensure it's covered by wildcard imports
5. Run tests and type checking before committing