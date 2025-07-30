#!/usr/bin/env python3

import asyncio
import sys
import re
from urllib.parse import urlparse
import click
from .main import OpenMemoryMCPBridge

@click.command()
@click.option('--sse', 'sse_url', 
              help='SSE endpoint URL (e.g., http://localhost:8765/mcp/claude/sse/moot)')
@click.option('--url', 'url', 
              help='Alternative way to specify the URL')
@click.option('--client', 'client', 
              help='Client name (e.g., claude, cursor)')
@click.option('--user-id', 'user_id', 
              help='User ID for the session')
@click.option('--base-url', 'base_url', 
              help='Base URL for OpenMemory API (e.g., http://localhost:8765)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
@click.version_option(version='0.1.0')
def main(sse_url, url, client, user_id, base_url, verbose):
    """
    OpenMemory MCP Bridge - A bridge between MCP clients and OpenMemory SSE endpoints.
    
    This tool acts as a replacement for supergateway, providing a direct connection
    to OpenMemory servers without the need for additional intermediaries.
    
    Examples:
        # Using SSE URL (similar to supergateway)
        openmemory-mcp-bridge --sse http://localhost:8765/mcp/claude/sse/moot
        
        # Using explicit parameters
        openmemory-mcp-bridge --base-url http://localhost:8765 --client claude --user-id moot
    """
    
    # Use url if sse_url is not provided
    if not sse_url and url:
        sse_url = url
    
    # Parse the SSE URL to extract components (only if CLI args not provided)
    if sse_url:
        parsed_url = urlparse(sse_url)
        if not base_url:
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Extract client and user_id from path only if not explicitly provided
        # Pattern: /mcp/{client}/sse/{user_id}
        path_pattern = r'/mcp/([^/]+)/sse/([^/]+)'
        match = re.match(path_pattern, parsed_url.path)
        
        if match:
            # Only use URL values if CLI args weren't provided
            if not client:
                client = match.group(1)
            if not user_id:
                user_id = match.group(2)
        else:
            click.echo(f"Error: Invalid SSE URL format. Expected: /mcp/{{client}}/sse/{{user_id}}", err=True)
            sys.exit(1)
    
    # Set defaults only if still not provided
    if not base_url:
        base_url = "http://localhost:8765"
    if not client:
        client = "claude"
    if not user_id:
        user_id = "default"
    
    # Validate required parameters
    if not base_url:
        click.echo("Error: Base URL is required. Use --base-url or --sse", err=True)
        sys.exit(1)
    
    if verbose:
        click.echo(f"Starting OpenMemory MCP Bridge", err=True)
        click.echo(f"  Base URL: {base_url}", err=True)
        click.echo(f"  Client: {client}", err=True)
        click.echo(f"  User ID: {user_id}", err=True)
    
    # Create and run the bridge
    bridge = OpenMemoryMCPBridge(base_url=base_url, client=client, user_id=user_id)
    
    try:
        asyncio.run(bridge.run_stdio())
    except KeyboardInterrupt:
        if verbose:
            click.echo("Shutting down...", err=True)
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 