# Claude Desktop Configuration Examples

This directory contains example Claude Desktop configurations for different QUADS server setups.

## Configuration Files

### `secure_ssl.json`
Use this configuration when your QUADS server has a valid SSL certificate from a trusted Certificate Authority.

**Features:**
- ✅ SSL certificate verification enabled
- ✅ Secure connection to QUADS server
- ✅ Recommended for production environments

### `self_signed_ssl.json` 
Use this configuration when your QUADS server uses self-signed SSL certificates.

**Features:**
- ⚠️ SSL certificate verification disabled
- ✅ Works with self-signed certificates
- ⚠️ Less secure - use only for trusted internal servers

## How to Use

1. **Choose the appropriate configuration** based on your QUADS server's SSL setup
2. **Copy the configuration** to your Claude Desktop settings
3. **Update the values** with your actual QUADS server details:
   - `command`: Update the path to your virtual environment
   - `cwd`: Update the path to your project directory
   - `MCP_QUADS__BASE_URL`: Your QUADS server URL
   - `MCP_QUADS__USERNAME`: Your QUADS username
   - `MCP_QUADS__PASSWORD`: Your QUADS password

## Claude Desktop Settings Location

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/claude/claude_desktop_config.json
```

## Alternative: Using .env File

Instead of putting credentials in the Claude Desktop config, you can use a `.env` file:

```json
{
  "mcpServers": {
    "quads-mcp": {
      "command": "/path/to/quads-mcp/.venv/bin/python",
      "args": ["-m", "quads_mcp.server"],
      "cwd": "/path/to/quads-mcp"
    }
  }
}
```

Then create a `.env` file in your project directory:

```bash
MCP_QUADS__BASE_URL=https://your-quads-server.com/api/v3
MCP_QUADS__USERNAME=your-username
MCP_QUADS__PASSWORD=your-password
MCP_QUADS__VERIFY_SSL=false  # Set to true for valid certificates
```

## Troubleshooting

### Server shows as disabled in Claude Desktop
- Check that the `command` path is correct
- Ensure the virtual environment exists and has all dependencies
- Verify the `cwd` path points to the project directory

### SSL certificate errors
- For self-signed certificates: Use `self_signed_ssl.json` config
- For certificate verification issues: Set `MCP_QUADS__VERIFY_SSL=false`
- For production: Use valid SSL certificates and `secure_ssl.json` config

### Authentication errors
- Verify your QUADS username and password are correct
- Check that the QUADS server URL is accessible
- Ensure the QUADS API is available at the specified endpoint