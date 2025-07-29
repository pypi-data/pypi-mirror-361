"""
QUADS MCP prompts implementation.
This file contains prompt templates for common QUADS operations.
"""

# Import these at the end to avoid circular imports
from ..server import mcp


@mcp.prompt()
def quads_host_search(search_criteria: str) -> str:
    """
    Prompt for searching and analyzing QUADS hosts.
    
    Args:
        search_criteria: The criteria to search for (model, name, status, etc.)
        
    Returns:
        A formatted prompt for host search and analysis
    """
    return f"""
    # QUADS Host Search and Analysis

    Please help me search for hosts in the QUADS system based on the following criteria:

    **Search Criteria**: {search_criteria}

    ## Tasks to Complete:

    1. **Search for hosts** using the appropriate QUADS tools with the specified criteria
    2. **Analyze the results** and provide a summary of:
       - Total number of hosts found
       - Host models and types
       - Current status (build, validated, broken, retired)
       - Cloud assignments
       - Hardware specifications (if detailed information is needed)

    3. **Provide recommendations** for:
       - Hosts suitable for new assignments
       - Hosts that may need maintenance
       - Capacity planning insights

    ## Available Tools:

    - `quads_get_hosts()` - Get all hosts with optional filtering
    - `quads_get_host_details()` - Get detailed information for specific hosts
    - `quads_get_available_hosts()` - Check host availability
    - `quads_check_host_availability()` - Check specific host availability

    Please start by searching for hosts matching the criteria and then provide your analysis.
    """


@mcp.prompt()
def quads_capacity_planning(requirements: str, timeframe: str = "next 30 days") -> str:
    """
    Prompt for QUADS capacity planning and resource allocation.
    
    Args:
        requirements: The capacity requirements to plan for
        timeframe: The timeframe for capacity planning
        
    Returns:
        A formatted prompt for capacity planning
    """
    return f"""
    # QUADS Capacity Planning Analysis

    Please help me analyze capacity and plan resource allocation for the QUADS system.

    **Requirements**: {requirements}
    **Timeframe**: {timeframe}

    ## Analysis Tasks:

    1. **Current Capacity Assessment**:
       - Get all available hosts and their specifications
       - Analyze current cloud assignments and utilization
       - Identify free clouds and resources

    2. **Future Availability Analysis**:
       - Check host availability for the specified timeframe
       - Analyze upcoming schedule changes and moves
       - Identify potential capacity constraints

    3. **Resource Matching**:
       - Match available resources to requirements
       - Consider hardware specifications (CPU, memory, storage, network)
       - Account for host types and models

    4. **Recommendations**:
       - Suggest optimal host assignments
       - Identify any capacity gaps
       - Recommend timeline for resource allocation

    ## Available Tools:

    - `quads_get_available_hosts()` - Check available hosts
    - `quads_get_free_clouds()` - Find available clouds
    - `quads_get_hosts()` - Get host specifications
    - `quads_get_current_schedules()` - Check current assignments
    - `quads_get_moves()` - Check upcoming transitions

    Please provide a comprehensive capacity analysis and recommendations.
    """


@mcp.prompt()
def quads_troubleshooting(issue_description: str) -> str:
    """
    Prompt for troubleshooting QUADS issues.
    
    Args:
        issue_description: Description of the issue to troubleshoot
        
    Returns:
        A formatted prompt for troubleshooting
    """
    return f"""
    # QUADS Troubleshooting

    I'm having an issue with the QUADS system that needs troubleshooting.

    **Issue Description**: {issue_description}

    Please help me troubleshoot this systematically by:

    1. **Gathering System Information**:
       - Check QUADS version and system status
       - Verify connectivity to the QUADS API
       - Review current system configuration

    2. **Analyzing the Problem**:
       - Examine related hosts, clouds, and assignments
       - Check schedules and availability
       - Look for any conflicts or inconsistencies

    3. **Identifying Root Cause**:
       - Correlate symptoms with system state
       - Check for common issues (network, permissions, scheduling conflicts)
       - Analyze timing and dependencies

    4. **Providing Solutions**:
       - Suggest specific remediation steps
       - Recommend preventive measures
       - Provide alternative approaches if needed

    Available diagnostic tools:
    - `quads_get_version()` - Check system version
    - `quads_get_hosts()` - Check host status
    - `quads_get_assignments()` - Review assignments
    - `quads_get_schedules()` - Check scheduling
    - `quads_get_moves()` - Check transitions

    Please start by gathering relevant system information and then provide your analysis.
    """


@mcp.prompt()
def quads_assignment_planning(cloud_name: str, requirements: str) -> str:
    """
    Prompt for planning QUADS cloud assignments.
    
    Args:
        cloud_name: Name of the cloud to plan assignment for
        requirements: Requirements for the assignment
        
    Returns:
        A formatted prompt for assignment planning
    """
    return f"""
    # QUADS Assignment Planning

    Please help me plan a cloud assignment in the QUADS system.

    **Cloud**: {cloud_name}
    **Requirements**: {requirements}

    ## Planning Tasks:

    1. **Cloud Analysis**:
       - Check if the cloud exists and is available
       - Review current cloud status and assignments
       - Verify cloud is free for new assignments

    2. **Host Selection**:
       - Find hosts that match the requirements
       - Check host availability for the desired timeframe
       - Verify host specifications meet requirements

    3. **Scheduling Validation**:
       - Check for scheduling conflicts
       - Verify no overlapping assignments
       - Confirm availability windows

    4. **Assignment Recommendations**:
       - Suggest optimal host-to-cloud mappings
       - Recommend assignment timeline
       - Identify any prerequisites or dependencies

    ## Available Tools:

    - `quads_get_clouds()` - Check cloud status
    - `quads_get_free_clouds()` - Find available clouds
    - `quads_get_available_hosts()` - Check host availability
    - `quads_get_current_schedules()` - Check existing schedules
    - `quads_get_active_assignments()` - Check active assignments

    Please provide a comprehensive assignment plan with specific recommendations.
    """


@mcp.prompt()
def quads_maintenance_planning(maintenance_type: str, affected_resources: str) -> str:
    """
    Prompt for planning QUADS maintenance operations.
    
    Args:
        maintenance_type: Type of maintenance to plan
        affected_resources: Resources that will be affected
        
    Returns:
        A formatted prompt for maintenance planning
    """
    return f"""
    # QUADS Maintenance Planning

    Please help me plan maintenance operations for the QUADS system.

    **Maintenance Type**: {maintenance_type}
    **Affected Resources**: {affected_resources}

    ## Planning Tasks:

    1. **Impact Assessment**:
       - Identify all affected hosts and resources
       - Check current assignments and schedules
       - Determine impact on active cloud environments

    2. **Scheduling Analysis**:
       - Find optimal maintenance windows
       - Check for conflicts with existing schedules
       - Identify minimum disruption periods

    3. **Dependency Mapping**:
       - Map dependencies between affected resources
       - Identify critical path items
       - Plan maintenance sequence

    4. **Communication Plan**:
       - Identify affected users and assignments
       - Determine notification requirements
       - Plan status updates and coordination

    ## Available Tools:

    - `quads_get_hosts()` - Check host status and assignments
    - `quads_get_active_assignments()` - Check affected assignments
    - `quads_get_current_schedules()` - Check scheduling conflicts
    - `quads_get_moves()` - Check planned transitions

    Please provide a detailed maintenance plan with timeline and impact analysis.
    """


@mcp.prompt()
def quads_reporting(report_type: str, scope: str = "all") -> str:
    """
    Prompt for generating QUADS reports.
    
    Args:
        report_type: Type of report to generate
        scope: Scope of the report (all, specific cloud, date range, etc.)
        
    Returns:
        A formatted prompt for report generation
    """
    return f"""
    # QUADS Report Generation

    Please help me generate a comprehensive report from the QUADS system.

    **Report Type**: {report_type}
    **Scope**: {scope}

    ## Report Requirements:

    1. **Data Collection**:
       - Gather relevant data from QUADS API
       - Ensure data completeness and accuracy
       - Include current timestamp for reference

    2. **Analysis and Summary**:
       - Provide executive summary
       - Highlight key metrics and trends
       - Identify notable patterns or issues

    3. **Detailed Breakdown**:
       - Organize data by relevant categories
       - Include detailed specifications where relevant
       - Provide context for numbers and status

    4. **Recommendations**:
       - Suggest actions based on findings
       - Highlight optimization opportunities
       - Identify potential issues or risks

    ## Available Data Sources:

    - `quads_get_hosts()` - Host inventory and status
    - `quads_get_clouds()` - Cloud environments
    - `quads_get_assignments()` - Assignment information
    - `quads_get_schedules()` - Scheduling data
    - `quads_get_available_hosts()` - Availability information

    Please generate a comprehensive report with clear formatting and actionable insights.
    """


@mcp.prompt()
def quads_health_check() -> str:
    """
    Prompt for performing QUADS system health checks.
    
    Returns:
        A formatted prompt for health checking
    """
    return """
    # QUADS System Health Check

    I need to perform a comprehensive health check of the QUADS system.

    Please perform a comprehensive health check by examining:

    1. **System Connectivity**:
       - Verify API connectivity and response times
       - Check system version and basic functionality
       - Test authentication if configured

    2. **Resource Status**:
       - Check host status (broken, retired, build issues)
       - Verify cloud configurations
       - Review assignment states

    3. **Scheduling Integrity**:
       - Check for scheduling conflicts
       - Verify assignment consistency
       - Look for orphaned or problematic schedules

    4. **Capacity and Utilization**:
       - Review resource utilization
       - Check available capacity
       - Identify underutilized resources

    5. **System Health Metrics**:
       - Count of healthy vs. problematic hosts
       - Assignment success rates
       - Resource availability trends

    Available diagnostic tools:
    - `quads_get_version()` - System version check
    - `quads_get_hosts()` - Host health status
    - `quads_get_clouds()` - Cloud configurations
    - `quads_get_assignments()` - Assignment states
    - `quads_get_schedules()` - Schedule integrity

    Please provide a detailed health report with recommendations for any issues found.
    """