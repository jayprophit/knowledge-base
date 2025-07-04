# MCP Configuration

## Overview
This directory contains configuration files for the Model Context Protocol (MCP) integration with the knowledge base. MCP enables AI assistants to access external tools, services, and data sources through standardized interfaces.

## Files

### mcp_config.json
The main configuration file that defines available MCP servers and their parameters. Each server provides specific functionality that can be used to enhance the knowledge base's capabilities.

## Usage

### Setting Up MCP Integration

1. Copy `mcp_config.json` to your local environment
2. Fill in any required API keys or authentication tokens
3. Modify file paths to match your local file system
4. Use with compatible MCP clients or AI systems

### Customizing Servers

You can customize the configuration by:

- Adding new servers to the `mcpServers` object
- Modifying command arguments for existing servers
- Setting environment variables for authentication
- Specifying file paths for local data access

### Example: Adding a Custom Server

```json
"custom-server": {
  "command": "npx",
  "args": [
    "-y",
    "your-custom-mcp-server"
  ],
  "env": {
    "CUSTOM_API_KEY": "your-api-key-here"
  }
}
```

## Security Considerations

- Never commit API keys or sensitive tokens to version control
- Use environment variables or secure storage for credentials
- Consider using `.env` files (added to `.gitignore`) for local development
- For deployment, use secure environment variable management

## Available Servers

The configuration includes servers for:

- Memory management
- Sequential thinking
- Web automation (Puppeteer)
- File system access
- Git operations
- HTTP requests
- Search functionality
- Mapping services
- Time-based operations
- Database access (PostgreSQL, SQLite)
- Third-party integrations (Notion, Google Drive, GitHub, etc.)

## Related Documents

- [MCP Integration Guide](../integration_guide.md)
- [API Documentation](../api/README.md)
- [Vectorization Protocols](../vectorization/README.md)
- [System Design](../../system_design.md)
