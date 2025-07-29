"""
QUADS MCP tools implementation.
This file contains tool implementations for the QUADS API operations.
"""

from typing import Dict, Any, Optional
import httpx

# Import these at the end to avoid circular imports  
from ..server import Context, mcp
from ..auth import get_auth_manager


async def make_quads_request(method: str, endpoint: str, ctx: Context, **kwargs) -> Dict[str, Any]:
    """
    Helper function to make authenticated requests to QUADS API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint (e.g., '/clouds/' or 'clouds/')
        ctx: Context for logging
        **kwargs: Additional arguments for the request
        
    Returns:
        JSON response as dictionary
    """
    auth_manager = get_auth_manager()
    
    if not auth_manager:
        error_msg = "Authentication manager not initialized"
        ctx.error(error_msg)
        return {"error": error_msg}
    
    if not auth_manager.has_credentials:
        error_msg = "No QUADS credentials configured. Please set MCP_QUADS__USERNAME/PASSWORD or MCP_QUADS__AUTH_TOKEN"
        ctx.error(error_msg)
        return {"error": error_msg}
    
    try:
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        ctx.debug(f"Making {method} request to QUADS: {endpoint}")
        
        response = await auth_manager.make_authenticated_request(method, endpoint, **kwargs)
        response.raise_for_status()
        
        return response.json()
        
    except httpx.HTTPStatusError as e:
        error_msg = f"QUADS API error {e.response.status_code}: {e.response.reason_phrase}"
        ctx.error(error_msg)
        return {"error": error_msg, "status_code": e.response.status_code}
    except Exception as e:
        error_msg = f"QUADS API request failed: {str(e)}"
        ctx.error(error_msg)
        return {"error": error_msg}


@mcp.tool()
async def quads_login(username: str, password: str, ctx: Context) -> Dict[str, Any]:
    """
    Manually login to QUADS API and get authentication token.
    
    Note: Authentication is normally handled automatically using credentials 
    from .env file. This tool is for manual login if needed.
    
    Args:
        username: Username for authentication
        password: Password for authentication
        ctx: The Context object (automatically injected)
        
    Returns:
        Authentication token and status
    """
    auth_manager = get_auth_manager()
    
    if not auth_manager:
        error_msg = "Authentication manager not initialized"
        ctx.error(error_msg)
        return {"error": error_msg}
    
    try:
        # Create a temporary auth manager for manual login
        from ..auth import QuadsAuthManager
        
        temp_auth = QuadsAuthManager(
            base_url=auth_manager.base_url,
            username=username,
            password=password,
            timeout=auth_manager.timeout
        )
        
        ctx.info(f"Manually logging in to QUADS API")
        
        # Force login
        await temp_auth._perform_login()
        
        ctx.info("Successfully logged in to QUADS")
        return {
            "auth_token": temp_auth._auth_token,
            "message": "Login successful",
            "note": "This token can be used in MCP_QUADS__AUTH_TOKEN environment variable"
        }
            
    except Exception as e:
        error_msg = f"Login error: {str(e)}"
        ctx.error(error_msg)
        return {"error": error_msg}


@mcp.tool()
async def quads_get_clouds(ctx: Context) -> Dict[str, Any]:
    """
    Get all defined clouds from QUADS.
    
    Args:
        ctx: The Context object (automatically injected)
        
    Returns:
        List of all clouds
    """
    ctx.info("Fetching all clouds from QUADS")
    
    result = await make_quads_request("GET", "/clouds/", ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} clouds")
        return {"clouds": result}
    
    return result


@mcp.tool()
async def quads_get_free_clouds(ctx: Context) -> Dict[str, Any]:
    """
    Get all free clouds available for new assignments.
    
    Args:
        ctx: The Context object (automatically injected)
        
    Returns:
        List of free clouds
    """
    ctx.info("Fetching free clouds from QUADS")
    
    result = await make_quads_request("GET", "/clouds/free/", ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} free clouds")
        return {"free_clouds": result}
    
    return result


@mcp.tool()
async def quads_get_hosts(name: Optional[str] = None, model: Optional[str] = None, 
                         host_type: Optional[str] = None, broken: Optional[bool] = None,
                         ctx: Context = None) -> Dict[str, Any]:
    """
    Get hosts from QUADS with optional filtering.
    
    Args:
        name: Filter hosts by name
        model: Filter hosts by model name
        host_type: Filter hosts by type
        broken: Filter by broken status
        ctx: The Context object (automatically injected)
        
    Returns:
        List of hosts matching the criteria
    """
    # Build query parameters
    params = {}
    if name:
        params['name'] = name
    if model:
        params['model'] = model
    if host_type:
        params['host_type'] = host_type
    if broken is not None:
        params['broken'] = str(broken).lower()
    
    ctx.info(f"Fetching hosts from QUADS with filters: {params}")
    
    result = await make_quads_request("GET", "/hosts/", ctx, params=params)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} hosts")
        return {"hosts": result, "filters": params}
    
    return result


@mcp.tool()
async def quads_get_host_details(hostname: str, ctx: Context) -> Dict[str, Any]:
    """
    Get detailed information about a specific host.
    
    Args:
        hostname: The hostname to get details for
        ctx: The Context object (automatically injected)
        
    Returns:
        Detailed host information including hardware specs
    """
    ctx.info(f"Fetching details for host: {hostname}")
    
    result = await make_quads_request("GET", f"/hosts/{hostname}/", ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved details for host {hostname}")
        return {"host": result}
    
    return result


@mcp.tool()
async def quads_get_available_hosts(start: Optional[str] = None, end: Optional[str] = None,
                                   cloud: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Get available hosts for a specific time period.
    
    Args:
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        cloud: Filter by cloud name
        ctx: The Context object (automatically injected)
        
    Returns:
        List of available hosts
    """
    params = {}
    if start:
        params['start'] = start
    if end:
        params['end'] = end
    if cloud:
        params['cloud'] = cloud
    
    ctx.info(f"Fetching available hosts with parameters: {params}")
    
    result = await make_quads_request("GET", "/available/", ctx, params=params)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} available hosts")
        return {"available_hosts": result, "parameters": params}
    
    return result


@mcp.tool()
async def quads_check_host_availability(hostname: str, start: Optional[str] = None, 
                                       end: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Check if a specific host is available for a given time period.
    
    Args:
        hostname: The hostname to check
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        ctx: The Context object (automatically injected)
        
    Returns:
        Host availability status
    """
    params = {}
    if start:
        params['start'] = start
    if end:
        params['end'] = end
    
    ctx.info(f"Checking availability for host {hostname} with parameters: {params}")
    
    result = await make_quads_request("GET", f"/available/{hostname}/", ctx, params=params)
    
    if "error" not in result:
        ctx.info(f"Checked availability for host {hostname}")
        return {"hostname": hostname, "availability": result, "parameters": params}
    
    return result


@mcp.tool()
async def quads_get_schedules(ctx: Context) -> Dict[str, Any]:
    """
    Get all defined schedules from QUADS.
    
    Args:
        ctx: The Context object (automatically injected)
        
    Returns:
        List of all schedules
    """
    ctx.info("Fetching all schedules from QUADS")
    
    result = await make_quads_request("GET", "/schedules/", ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} schedules")
        return {"schedules": result}
    
    return result


@mcp.tool()
async def quads_get_current_schedules(date: Optional[str] = None, host: Optional[str] = None,
                                     cloud: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Get current schedules with optional filtering.
    
    Args:
        date: Date to check current schedules for
        host: Filter by hostname
        cloud: Filter by cloud name
        ctx: The Context object (automatically injected)
        
    Returns:
        List of current schedules
    """
    params = {}
    if date:
        params['date'] = date
    if host:
        params['host'] = host
    if cloud:
        params['cloud'] = cloud
    
    ctx.info(f"Fetching current schedules with parameters: {params}")
    
    result = await make_quads_request("GET", "/schedules/current/", ctx, params=params)
    
    if "error" not in result:
        ctx.info(f"Retrieved current schedules")
        return {"current_schedules": result, "parameters": params}
    
    return result


@mcp.tool()
async def quads_get_assignments(ctx: Context) -> Dict[str, Any]:
    """
    Get all assignments from QUADS.
    
    Args:
        ctx: The Context object (automatically injected)
        
    Returns:
        List of all assignments
    """
    ctx.info("Fetching all assignments from QUADS")
    
    result = await make_quads_request("GET", "/assignments/", ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved assignments")
        return {"assignments": result}
    
    return result


@mcp.tool()
async def quads_get_active_assignments(cloud_name: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Get active assignments, optionally filtered by cloud.
    
    Args:
        cloud_name: Filter by specific cloud name
        ctx: The Context object (automatically injected)
        
    Returns:
        List of active assignments
    """
    if cloud_name:
        endpoint = f"/assignments/active/{cloud_name}/"
        ctx.info(f"Fetching active assignments for cloud: {cloud_name}")
    else:
        endpoint = "/assignments/active/"
        ctx.info("Fetching all active assignments")
    
    result = await make_quads_request("GET", endpoint, ctx)
    
    if "error" not in result:
        ctx.info(f"Retrieved active assignments")
        return {"active_assignments": result, "cloud_filter": cloud_name}
    
    return result


@mcp.tool()
async def quads_get_moves(date: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Get host moves/transitions for a specific date.
    
    Args:
        date: Date to get moves for (YYYY-MM-DD format)
        ctx: The Context object (automatically injected)
        
    Returns:
        List of host moves
    """
    params = {}
    if date:
        params['date'] = date
    
    ctx.info(f"Fetching moves with parameters: {params}")
    
    result = await make_quads_request("GET", "/moves/", ctx, params=params)
    
    if "error" not in result:
        ctx.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} moves")
        return {"moves": result, "parameters": params}
    
    return result


@mcp.tool()
async def quads_get_version(ctx: Context) -> Dict[str, Any]:
    """
    Get QUADS version information.
    
    Args:
        ctx: The Context object (automatically injected)
        
    Returns:
        QUADS version information
    """
    ctx.info("Fetching QUADS version")
    
    result = await make_quads_request("GET", "/version/", ctx)
    
    if "error" not in result:
        ctx.info("Retrieved QUADS version")
        return {"version": result}
    
    return result