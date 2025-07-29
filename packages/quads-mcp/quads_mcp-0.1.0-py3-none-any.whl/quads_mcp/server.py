"""
Main MCP server implementation.
This file initializes the FastMCP server and imports all tools, resources, and prompts.
"""

import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

# Import config management
from .config import load_config
from .auth import QuadsAuthManager, set_auth_manager


@dataclass
class AppContext:
    """
    Type-safe application context container.
    Store any application-wide state or connections here.
    """
    config: dict


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Application lifecycle manager.
    Handles startup and shutdown operations with proper resource management.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        The application context with initialized resources
    """
    # Load configuration
    config = load_config()
    
    # Initialize QUADS authentication manager
    quads_config = config.get('quads', {})
    auth_manager = QuadsAuthManager(
        base_url=quads_config.get('base_url', 'https://quads.example.com/api/v3'),
        username=quads_config.get('username'),
        password=quads_config.get('password'),
        auth_token=quads_config.get('auth_token'),
        timeout=quads_config.get('timeout', 30),
        verify_ssl=quads_config.get('verify_ssl', True)
    )
    
    # Set the global auth manager for tools to use
    set_auth_manager(auth_manager)
    
    # Initialize connections and resources
    print("🚀 Server starting up...")
    if auth_manager.has_credentials:
        if auth_manager.username:
            print(f"📡 QUADS API: {quads_config.get('base_url')} (user: {auth_manager.username})")
        else:
            print(f"📡 QUADS API: {quads_config.get('base_url')} (token auth)")
    else:
        print("⚠️  No QUADS credentials configured - API calls will not be authenticated")
    
    try:
        # Create and yield the app context
        yield AppContext(config=config)
    finally:
        # Clean up resources on shutdown
        print("🛑 Server shutting down...")
        if auth_manager:
            await auth_manager.logout()


# Create the MCP server with lifespan support
mcp = FastMCP(
    "quads-mcp",  # Server name
    lifespan=app_lifespan,           # Lifecycle manager
    dependencies=["mcp>=1.0"],       # Required dependencies
)

# Import all tools, resources, and prompts
# These imports must come after the MCP server is initialized
from .tools.quads_tools import *
from .resources.quads_resources import *
from .prompts.quads_prompts import *

# Make the server instance accessible to other modules
server = mcp


def main():
    """
    Main entry point for the QUADS MCP server.
    This function is used by the console script and uvx.
    """
    mcp.run()


if __name__ == "__main__":
    # When executed directly, run the server
    main()