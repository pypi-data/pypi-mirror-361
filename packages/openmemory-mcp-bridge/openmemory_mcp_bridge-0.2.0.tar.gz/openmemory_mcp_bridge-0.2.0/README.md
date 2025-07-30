# OpenMemory MCP Bridge

A Model Context Protocol (MCP) bridge for OpenMemory SSE endpoints that provides a direct connection between MCP clients (like Claude Desktop, Cursor, etc.) and OpenMemory servers without requiring intermediaries like supergateway.

## Features

- **Direct Connection**: Connects directly to OpenMemory SSE endpoints without intermediaries
- **Dynamic Parameters**: Supports dynamic client and user ID parameters
- **MCP Protocol**: Implements the MCP protocol for seamless integration with MCP clients
- **Tool Support**: Provides access to OpenMemory's memory management tools
- **CLI Interface**: Easy-to-use command-line interface

## Installation

No installation required! Use `uvx` to run directly:

```bash
uvx openmemory-mcp-bridge --sse http://localhost:8765/mcp/{client}/sse/{userid}
```

## Usage

### Basic Usage (Similar to supergateway)

```bash
openmemory-mcp-bridge --sse http://localhost:8765/mcp/claude/sse/moot
```

### Using Explicit Parameters

```bash
openmemory-mcp-bridge --base-url http://localhost:8765 --client claude --user-id userid
```

### Command Line Options

- `--sse URL`: SSE endpoint URL (e.g., `http://localhost:8765/mcp/claude/sse/moot`)
- `--url URL`: Alternative way to specify the URL
- `--client NAME`: Client name (e.g., `claude`, `cursor`) - **explicit CLI args take precedence over URL parsing**
- `--user-id ID`: User ID for the session - **explicit CLI args take precedence over URL parsing**
- `--base-url URL`: Base URL for OpenMemory API (e.g., `http://localhost:8765`)
- `--verbose, -v`: Enable verbose logging
- `--help`: Show help message

**Note**: Explicit CLI arguments (`--client`, `--user-id`) take precedence over values parsed from the SSE URL. This allows you to override the client and user ID even when using the `--sse` option.

## Integration with MCP Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openmemory": {
      "command": "uvx",
      "args": [
        "openmemory-mcp-bridge",
        "--sse",
        "http://localhost:8765/mcp/claude/sse/moot"
      ]
    }
  }
}
```

### Cursor

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "openmemory": {
      "command": "uvx",
      "args": [
        "openmemory-mcp-bridge",
        "--sse",
        "http://localhost:8765/mcp/cursor/sse/moot"
      ]
    }
  }
}
```

### Using Explicit Parameters

You can also use explicit parameters instead of the SSE URL:

```json
{
  "mcpServers": {
    "openmemory": {
      "command": "uvx",
      "args": [
        "openmemory-mcp-bridge",
        "--base-url",
        "http://localhost:8765",
        "--client",
        "claude",
        "--user-id",
        "moot"
      ]
    }
  }
}
```

## Available Tools

The bridge provides access to the following OpenMemory tools:

- **add_memories**: Add new memories to the user's memory store
- **get_memories**: Retrieve memories based on a search query
- **delete_memories**: Delete specific memories by ID
- **delete_all_memories**: Delete all memories for a user
- **get_memory_history**: Get the history of memory operations

## URL Format

The SSE endpoint URL should follow this pattern:
```
http://localhost:8765/mcp/{client}/sse/{user_id}
```

Where:
- `{client}`: The client name (e.g., `claude`, `cursor`)
- `{user_id}`: The user identifier (e.g., `moot`)

## Why Use This Instead of Supergateway?

- **Direct Connection**: No intermediary proxy reducing potential points of failure
- **OpenMemory Specific**: Optimized for OpenMemory's API endpoints
- **Better Error Handling**: Provides detailed error messages and logging
- **Flexible Configuration**: Multiple ways to specify connection parameters
- **Maintained**: Actively maintained as part of the OpenMemory ecosystem

## Development

To develop this package:

1. Clone the repository
2. Install dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Build package: `python -m build`

## License

MIT License - see LICENSE file for details. 