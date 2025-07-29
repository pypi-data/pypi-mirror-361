"""
QUADS MCP resources implementation.
This file contains resource implementations for accessing QUADS data.
"""

import json
import datetime

# Import these at the end to avoid circular imports
from ..server import mcp


@mcp.resource("quads://clouds")
def quads_clouds_resource() -> str:
    """
    Resource for accessing QUADS cloud information.
    
    Returns:
        Cloud data formatted as markdown
    """
    return """
    # QUADS Clouds Resource
    
    This resource provides access to QUADS cloud environment information.
    
    ## Available Data
    
    - **All Clouds**: Complete list of defined clouds
    - **Free Clouds**: Clouds available for new assignments
    - **Cloud Summary**: Detailed cloud information including counts and owners
    
    ## Usage
    
    Use the QUADS tools to fetch real-time cloud data:
    
    ```
    quads_get_clouds()          # Get all clouds
    quads_get_free_clouds()     # Get available clouds
    ```
    
    ## Cloud Properties
    
    - **name**: Cloud identifier
    - **last_redefined**: Date of last cloud redefinition
    - **count**: Number of hosts in cloud
    - **description**: Cloud description
    - **owner**: Cloud owner
    - **ticket**: Associated ticket number
    - **provisioned**: Provisioning status
    - **validated**: Validation status
    """


@mcp.resource("quads://hosts")
def quads_hosts_resource() -> str:
    """
    Resource for accessing QUADS host information.
    
    Returns:
        Host data formatted as markdown
    """
    return """
    # QUADS Hosts Resource
    
    This resource provides access to QUADS physical host information.
    
    ## Available Data
    
    - **All Hosts**: Complete inventory of physical servers
    - **Host Details**: Detailed specifications including hardware
    - **Host Filtering**: Search by name, model, type, status
    - **Hardware Components**: Interfaces, disks, memory, processors
    
    ## Usage
    
    Use the QUADS tools to fetch real-time host data:
    
    ```
    quads_get_hosts()                    # Get all hosts
    quads_get_hosts(model="r640")        # Filter by model
    quads_get_hosts(broken=False)        # Filter by status
    quads_get_host_details("hostname")   # Get detailed specs
    ```
    
    ## Host Properties
    
    - **name**: Hostname/FQDN
    - **model**: Server model (e.g., r640, r740)
    - **host_type**: Type classification
    - **build**: Build status
    - **validated**: Validation status
    - **switch_config_applied**: Network configuration status
    - **broken**: Broken/maintenance status
    - **retired**: Retirement status
    - **last_build**: Last build date
    - **cloud_id**: Current cloud assignment
    - **interfaces**: Network interfaces
    - **disks**: Storage devices
    - **memory**: RAM modules
    - **processors**: CPU information
    """


@mcp.resource("quads://schedules")
def quads_schedules_resource() -> str:
    """
    Resource for accessing QUADS scheduling information.
    
    Returns:
        Schedule data formatted as markdown
    """
    return """
    # QUADS Schedules Resource
    
    This resource provides access to QUADS scheduling and reservation information.
    
    ## Available Data
    
    - **All Schedules**: Complete schedule database
    - **Current Schedules**: Currently active schedules
    - **Future Schedules**: Upcoming reservations
    - **Host Ranges**: Schedule data for date ranges
    
    ## Usage
    
    Use the QUADS tools to fetch real-time schedule data:
    
    ```
    quads_get_schedules()                    # Get all schedules
    quads_get_current_schedules()            # Get current schedules
    quads_get_current_schedules(host="h1")   # Filter by host
    quads_get_current_schedules(cloud="c1")  # Filter by cloud
    ```
    
    ## Schedule Properties
    
    - **start**: Schedule start date/time
    - **end**: Schedule end date/time
    - **build_start**: Build start date/time
    - **build_end**: Build end date/time
    - **assignment_id**: Associated assignment ID
    - **host_id**: Host identifier
    
    ## Date Formats
    
    Use ISO 8601 format for dates: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`
    """


@mcp.resource("quads://assignments")
def quads_assignments_resource() -> str:
    """
    Resource for accessing QUADS assignment information.
    
    Returns:
        Assignment data formatted as markdown
    """
    return """
    # QUADS Assignments Resource
    
    This resource provides access to QUADS cloud assignment information.
    
    ## Available Data
    
    - **All Assignments**: Complete assignment database
    - **Active Assignments**: Currently active assignments
    - **Cloud Assignments**: Assignments for specific clouds
    - **Assignment Details**: Detailed assignment information
    
    ## Usage
    
    Use the QUADS tools to fetch real-time assignment data:
    
    ```
    quads_get_assignments()                    # Get all assignments
    quads_get_active_assignments()             # Get active assignments
    quads_get_active_assignments("cloud01")   # Get assignments for specific cloud
    ```
    
    ## Assignment Properties
    
    - **active**: Assignment active status
    - **provisioned**: Provisioning status
    - **validated**: Validation status
    - **is_self_schedule**: Self-scheduling flag
    - **description**: Assignment description
    - **owner**: Assignment owner
    - **ticket**: Associated ticket number
    - **qinq**: QinQ VLAN configuration
    - **wipe**: Wipe configuration
    - **ccuser**: CC users list
    - **cloud_id**: Associated cloud ID
    - **vlan_id**: VLAN assignment
    """


@mcp.resource("quads://availability")
def quads_availability_resource() -> str:
    """
    Resource for accessing QUADS host availability information.
    
    Returns:
        Availability data formatted as markdown
    """
    return """
    # QUADS Availability Resource
    
    This resource provides access to QUADS host availability information.
    
    ## Available Data
    
    - **Available Hosts**: Hosts available for specific time periods
    - **Host Availability**: Check specific host availability
    - **Date Range Queries**: Availability for custom date ranges
    - **Cloud Filtering**: Availability by cloud type
    
    ## Usage
    
    Use the QUADS tools to check host availability:
    
    ```
    quads_get_available_hosts()                          # Get all available hosts
    quads_get_available_hosts(start="2024-01-01")       # From specific date
    quads_get_available_hosts(start="2024-01-01", 
                             end="2024-01-31")          # Date range
    quads_check_host_availability("hostname")           # Check specific host
    ```
    
    ## Parameters
    
    - **start**: Start date (YYYY-MM-DD format)
    - **end**: End date (YYYY-MM-DD format)
    - **cloud**: Filter by cloud name
    - **hostname**: Specific host to check
    
    ## Use Cases
    
    - Planning new assignments
    - Checking host maintenance windows
    - Capacity planning
    - Scheduling validation
    """


@mcp.resource("quads://moves")
def quads_moves_resource() -> str:
    """
    Resource for accessing QUADS host transition information.
    
    Returns:
        Move data formatted as markdown
    """
    return """
    # QUADS Moves Resource
    
    This resource provides access to QUADS host transition/move information.
    
    ## Available Data
    
    - **Host Moves**: Hosts transitioning between clouds
    - **Date-specific Moves**: Moves for specific dates
    - **Source/Target Clouds**: Origin and destination cloud information
    
    ## Usage
    
    Use the QUADS tools to fetch move information:
    
    ```
    quads_get_moves()                    # Get all moves
    quads_get_moves(date="2024-01-15")   # Get moves for specific date
    ```
    
    ## Move Properties
    
    - **host**: Hostname being moved
    - **new**: Target cloud name
    - **current**: Source cloud name
    
    ## Use Cases
    
    - Tracking host transitions
    - Planning network changes
    - Monitoring cloud reconfigurations
    - Scheduling coordination
    """


@mcp.resource("quads://config/{section}")
def quads_config_resource(section: str) -> str:
    """
    Resource for accessing QUADS configuration information.
    
    Args:
        section: Configuration section to access
        
    Returns:
        Configuration data formatted as markdown
    """
    # Access the app context
    ctx = mcp.get_request_context()
    config = ctx.lifespan_context.config
    
    # Check if the section exists
    if section in config:
        return f"""
        # QUADS Configuration: {section}
        
        ```json
        {json.dumps(config[section], indent=2)}
        ```
        """
    else:
        available_sections = list(config.keys()) if config else []
        return f"""
        # QUADS Configuration: {section}
        
        **Section not found.**
        
        Available configuration sections:
        {', '.join(available_sections) if available_sections else 'No configuration sections available'}
        
        ## Configuration Structure
        
        The QUADS MCP server supports the following configuration options:
        
        - **quads**: QUADS API configuration
          - **base_url**: QUADS API base URL
          - **auth_token**: Authentication token
          - **timeout**: Request timeout
        
        - **server**: Server configuration
          - **name**: Server name
          - **version**: Server version
        
        ## Environment Variables
        
        Configuration can be provided via environment variables:
        
        - `MCP_QUADS__BASE_URL`: QUADS API base URL
        - `MCP_QUADS__AUTH_TOKEN`: Authentication token
        - `MCP_CONFIG_FILE`: Path to JSON configuration file
        """


@mcp.resource("quads://hardware/{hostname}")
def quads_hardware_resource(hostname: str) -> str:
    """
    Resource template for accessing hardware information for a specific host.
    
    Args:
        hostname: The hostname to get hardware information for
        
    Returns:
        Hardware information formatted as markdown
    """
    return f"""
    # QUADS Hardware Resource: {hostname}
    
    This resource provides access to detailed hardware information for host `{hostname}`.
    
    ## Available Hardware Data
    
    Use the QUADS tools to fetch real-time hardware data:
    
    ```
    quads_get_host_details("{hostname}")
    ```
    
    ## Hardware Components
    
    ### Interfaces
    - Network interface details
    - MAC addresses
    - Switch connections
    - Port mappings
    - Speed specifications
    
    ### Disks
    - Storage device information
    - Disk types (SSD, HDD, NVMe)
    - Capacity specifications
    - Device counts
    
    ### Memory
    - RAM module information
    - Memory capacity
    - Module handles
    - Memory configuration
    
    ### Processors
    - CPU information
    - Core and thread counts
    - Processor models
    - Vendor information
    
    ## Usage Examples
    
    ```
    # Get complete host details including hardware
    quads_get_host_details("{hostname}")
    
    # Get specific hardware components
    # (Use the host details response to access hardware arrays)
    ```
    
    Generated at: {datetime.datetime.now().isoformat()}
    """