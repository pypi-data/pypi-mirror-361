# SSL Certificate Configuration

This document explains how to configure the QUADS MCP server to work with self-signed SSL certificates.

## Problem

When your QUADS server uses self-signed SSL certificates, the MCP client will fail to connect with SSL verification errors like:

```
SSL: CERTIFICATE_VERIFY_FAILED
```

## Solution

Configure the MCP server to disable SSL certificate verification by setting `verify_ssl` to `false`.

## Configuration Options

### Option 1: Environment Variables

Set the SSL verification option via environment variable:

```bash
export MCP_QUADS__VERIFY_SSL=false
```

### Option 2: Claude Desktop Configuration

Update your Claude Desktop MCP server configuration:

```json
{
  "mcpServers": {
    "quads-mcp": {
      "command": "/path/to/quads-mcp/.venv/bin/python",
      "args": ["-m", "quads_mcp.server"],
      "cwd": "/path/to/quads-mcp",
      "env": {
        "MCP_QUADS__BASE_URL": "https://your-quads-server.com/api/v3",
        "MCP_QUADS__USERNAME": "your-username", 
        "MCP_QUADS__PASSWORD": "your-password",
        "MCP_QUADS__VERIFY_SSL": "false"
      }
    }
  }
}
```

### Option 3: .env File

Create or update your `.env` file:

```bash
# QUADS API Configuration
MCP_QUADS__BASE_URL=https://your-quads-server.com/api/v3
MCP_QUADS__USERNAME=your-username
MCP_QUADS__PASSWORD=your-password

# Disable SSL verification for self-signed certificates
MCP_QUADS__VERIFY_SSL=false
```

### Option 4: JSON Configuration File

Create a config file (e.g., `config.json`):

```json
{
  "quads": {
    "base_url": "https://your-quads-server.com/api/v3",
    "username": "your-username",
    "password": "your-password",
    "verify_ssl": false
  }
}
```

Then set the config file path:

```bash
export MCP_CONFIG_FILE=/path/to/config.json
```

## Valid Values

The `verify_ssl` option accepts the following values (case-insensitive):

- **Enable SSL verification** (default): `true`, `yes`, `1`
- **Disable SSL verification**: `false`, `no`, `0`

## Security Considerations

⚠️ **Warning**: Disabling SSL certificate verification reduces security by making your connections vulnerable to man-in-the-middle attacks.

### When to disable SSL verification:

- ✅ Internal/development QUADS servers with self-signed certificates
- ✅ Testing environments 
- ✅ Controlled network environments

### When to keep SSL verification enabled:

- ✅ Production environments with proper SSL certificates
- ✅ Public-facing QUADS servers
- ✅ Any environment where security is critical

## Alternative Solutions

Instead of disabling SSL verification, consider these more secure alternatives:

### 1. Add Certificate to Trust Store

Add your QUADS server's certificate to your system's trust store:

```bash
# Linux (Ubuntu/Debian)
sudo cp your-quads-cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# macOS
sudo security add-trusted-cert -d root -r trustRoot -k /Library/Keychains/System.keychain your-quads-cert.crt
```

### 2. Use Proper SSL Certificates

Configure your QUADS server with proper SSL certificates from a trusted CA:

- Use Let's Encrypt for free certificates
- Purchase certificates from a commercial CA
- Use internal CA certificates if available

### 3. Certificate Pinning (Advanced)

For advanced users, you can modify the authentication manager to pin specific certificates instead of disabling all verification.

## Testing SSL Configuration

Test your SSL configuration:

```bash
# Test with SSL verification enabled (default)
MCP_QUADS__VERIFY_SSL=true python test_server.py

# Test with SSL verification disabled
MCP_QUADS__VERIFY_SSL=false python test_server.py
```

## Troubleshooting

### Common SSL Errors

1. **CERTIFICATE_VERIFY_FAILED**: Set `verify_ssl=false`
2. **SSL_WRONG_VERSION_NUMBER**: Check if URL uses HTTPS
3. **HOSTNAME_VERIFICATION_FAILED**: Ensure hostname matches certificate
4. **CERT_HAS_EXPIRED**: Update certificate or disable verification

### Debug SSL Issues

Enable debug logging to see SSL-related errors:

```bash
export MCP_DEBUG=true
export MCP_LOG_LEVEL=debug
```

### Verify Configuration

Check that your SSL configuration is being loaded correctly:

```bash
python -c "
from quads_mcp.config import load_config
config = load_config()
print('SSL verification:', config.get('quads', {}).get('verify_ssl', True))
"
```

Should output:
```
SSL verification: False
```