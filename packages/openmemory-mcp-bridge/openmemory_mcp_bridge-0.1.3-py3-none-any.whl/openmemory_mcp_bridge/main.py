#!/usr/bin/env python3

import asyncio
import json
import sys
import httpx
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenMemoryMCPBridge:
    """MCP Bridge for OpenMemory SSE endpoints"""
    
    def __init__(self, base_url: str, client: str = "claude", user_id: str = "default"):
        """
        Initialize the MCP bridge.
        
        Args:
            base_url: Base URL for OpenMemory API (e.g., http://localhost:8765)
            client: Client name (e.g., claude, cursor)
            user_id: User ID for the session
        """
        self.base_url = base_url.rstrip('/')
        self.client = client
        self.user_id = user_id
        self.sse_url = f"{self.base_url}/mcp/{self.client}/sse/{self.user_id}"
        self.message_url = f"{self.sse_url}/messages/"
        self.session_id = None
        self.is_initialized = False
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Define the tools that OpenMemory provides
        self.tools = [
            {
                "name": "add_memories",
                "description": "Add a new memory. This method is called everytime the user informs anything about themselves, their preferences, or anything that has any relevant information which can be useful in the future conversation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of memories to add"
                        }
                    },
                    "required": ["memories"]
                }
            },
            {
                "name": "get_memories",
                "description": "Get memories for a user based on a query. This method is called everytime before answering user queries to understand user's preferences and history.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to search for memories"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "delete_memories",
                "description": "Delete memories for a user based on memory IDs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of memory IDs to delete"
                        }
                    },
                    "required": ["memory_ids"]
                }
            },
            {
                "name": "delete_all_memories",
                "description": "Delete all memories for a user.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_memory_history",
                "description": "Get the history of memory operations for a user.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def initialize(self):
        """Initialize the MCP server"""
        try:
            logger.info(f"Initializing OpenMemory MCP Bridge for {self.client}/{self.user_id}")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        await self.initialize()
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "listChanged": True
                },
                "prompts": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "openmemory-mcp-bridge",
                "version": "0.1.3"
            }
        }

    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": self.tools
        }

    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": []
        }

    async def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {
            "prompts": []
        }

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        try:
            if tool_name == "add_memories":
                result = await self._add_memories(arguments)
            elif tool_name == "get_memories":
                result = await self._get_memories(arguments)
            elif tool_name == "delete_memories":
                result = await self._delete_memories(arguments)
            elif tool_name == "delete_all_memories":
                result = await self._delete_all_memories(arguments)
            elif tool_name == "get_memory_history":
                result = await self._get_memory_history(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def _add_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add memories to OpenMemory"""
        memories = arguments.get("memories", [])
        
        # OpenMemory API expects individual memory creation calls
        results = []
        for memory_text in memories:
            payload = {
                "user_id": self.user_id,
                "text": memory_text,
                "infer": False,
                "app": self.client
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/api/v1/memories/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            results.append(response.json())
        
        return {"results": results, "count": len(results)}

    async def _get_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memories from OpenMemory"""
        query = arguments.get("query", "")
        
        # Use the filter endpoint for search queries
        payload = {
            "user_id": self.user_id,
            "page": 1,
            "size": 20,
            "search_query": query if query else None,
            "show_archived": False
        }
        
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/filter",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _delete_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete specific memories from OpenMemory"""
        memory_ids = arguments.get("memory_ids", [])
        
        payload = {
            "memory_ids": memory_ids,
            "user_id": self.user_id
        }
        
        response = await self.http_client.delete(
            f"{self.base_url}/api/v1/memories/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _delete_all_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete all memories for a user"""
        # First, get all memories
        memories_response = await self._get_memories({"query": ""})
        
        if "items" in memories_response:
            memory_ids = [memory["id"] for memory in memories_response["items"]]
            
            if memory_ids:
                # Delete all memories using the regular delete endpoint
                return await self._delete_memories({"memory_ids": memory_ids})
            else:
                return {"message": "No memories found to delete", "count": 0}
        else:
            return {"message": "No memories found to delete", "count": 0}

    async def _get_memory_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory history for a user"""
        # Get all memories sorted by creation date (acts as history)
        payload = {
            "user_id": self.user_id,
            "page": 1,
            "size": 50,
            "sort_column": "created_at",
            "sort_direction": "desc",
            "show_archived": True  # Include archived memories in history
        }
        
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/filter",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        # Format as history
        return {
            "history": result.get("items", []),
            "total": result.get("total", 0),
            "message": "Memory history (sorted by creation date)"
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"Handling request: {method}")
        
        if method == "initialize":
            result = await self.handle_initialize(params)
        elif method == "tools/list":
            result = await self.handle_tools_list(params)
        elif method == "tools/call":
            result = await self.handle_tools_call(params)
        elif method == "resources/list":
            result = await self.handle_resources_list(params)
        elif method == "prompts/list":
            result = await self.handle_prompts_list(params)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }

    async def run_stdio(self):
        """Run the MCP server over stdio"""
        logger.info(f"Starting OpenMemory MCP Bridge over stdio for {self.client}/{self.user_id}")
        
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # Write JSON-RPC response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            logger.info("Shutting down OpenMemory MCP Bridge")
        finally:
            await self.http_client.aclose()

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'http_client') and self.http_client:
            asyncio.create_task(self.http_client.aclose()) 