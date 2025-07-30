#!/usr/bin/env python3

import asyncio
import json
import sys
import httpx
import logging
import importlib.metadata
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_version():
    try:
        return importlib.metadata.version("openmemory-mcp-bridge")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"

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
            },
            {
                "name": "get_memory_by_id",
                "description": "Get a specific memory by its ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The ID of the memory to retrieve"
                        }
                    },
                    "required": ["memory_id"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update the content of a specific memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The ID of the memory to update"
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content for the memory"
                        }
                    },
                    "required": ["memory_id", "content"]
                }
            },
            {
                "name": "get_categories",
                "description": "Get all available memory categories for the user.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "archive_memories",
                "description": "Archive memories (they will be hidden from normal searches but not deleted).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of memory IDs to archive"
                        }
                    },
                    "required": ["memory_ids"]
                }
            },
            {
                "name": "get_related_memories",
                "description": "Get memories related to a specific memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The ID of the memory to find related memories for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of related memories to return (default: 10)",
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["memory_id"]
                }
            },
            {
                "name": "get_user_stats",
                "description": "Get user statistics including total memories and apps.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_apps",
                "description": "List all apps associated with the user.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "is_active": {
                            "type": "boolean",
                            "description": "Filter by active status (optional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "search_memories",
                "description": "Advanced search for memories with filtering options.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by categories"
                        },
                        "from_date": {
                            "type": "integer",
                            "description": "Filter memories created after this timestamp"
                        },
                        "to_date": {
                            "type": "integer",
                            "description": "Filter memories created before this timestamp"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort by field (created_at, content, etc.)",
                            "enum": ["created_at", "content"]
                        },
                        "sort_direction": {
                            "type": "string",
                            "description": "Sort direction",
                            "enum": ["asc", "desc"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 20)",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "show_archived": {
                            "type": "boolean",
                            "description": "Include archived memories in results (default: false)"
                        }
                    },
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
                "version": get_version()
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
            elif tool_name == "get_memory_by_id":
                result = await self._get_memory_by_id(arguments)
            elif tool_name == "update_memory":
                result = await self._update_memory(arguments)
            elif tool_name == "get_categories":
                result = await self._get_categories(arguments)
            elif tool_name == "archive_memories":
                result = await self._archive_memories(arguments)
            elif tool_name == "get_related_memories":
                result = await self._get_related_memories(arguments)
            elif tool_name == "get_user_stats":
                result = await self._get_user_stats(arguments)
            elif tool_name == "list_apps":
                result = await self._list_apps(arguments)
            elif tool_name == "search_memories":
                result = await self._search_memories(arguments)
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
            "size": 50,
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

    async def _get_memory_by_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific memory by ID"""
        memory_id = arguments.get("memory_id")
        
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/memories/{memory_id}",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific memory"""
        memory_id = arguments.get("memory_id")
        content = arguments.get("content")
        
        payload = {
            "memory_content": content,
            "user_id": self.user_id
        }
        
        response = await self.http_client.put(
            f"{self.base_url}/api/v1/memories/{memory_id}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_categories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all categories for the user"""
        params = {"user_id": self.user_id}
        
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/memories/categories",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _archive_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Archive memories"""
        memory_ids = arguments.get("memory_ids", [])
        
        # Convert string IDs to UUIDs for the API
        uuid_ids = [memory_id for memory_id in memory_ids]
        
        payload = {
            "memory_ids": uuid_ids,
            "user_id": self.user_id
        }
        
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/actions/archive",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_related_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get related memories for a specific memory"""
        memory_id = arguments.get("memory_id")
        limit = arguments.get("limit", 10)
        
        params = {
            "user_id": self.user_id,
            "size": limit
        }
        
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/memories/{memory_id}/related",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _get_user_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get user statistics"""
        params = {"user_id": self.user_id}
        
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/stats/",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _list_apps(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all apps for the user"""
        params = {}
        
        is_active = arguments.get("is_active")
        if is_active is not None:
            params["is_active"] = is_active
        
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/apps/",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _search_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced search for memories with filtering"""
        query = arguments.get("query", "")
        categories = arguments.get("categories", [])
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        sort_by = arguments.get("sort_by", "created_at")
        sort_direction = arguments.get("sort_direction", "desc")
        limit = arguments.get("limit", 20)
        show_archived = arguments.get("show_archived", False)
        
        payload = {
            "user_id": self.user_id,
            "page": 1,
            "size": limit,
            "search_query": query if query else None,
            "sort_column": sort_by,
            "sort_direction": sort_direction,
            "show_archived": show_archived
        }
        
        if categories:
            # Note: The API might expect category_ids, but we'll try with category names first
            payload["categories"] = ",".join(categories)
        
        if from_date:
            payload["from_date"] = from_date
        
        if to_date:
            payload["to_date"] = to_date
        
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/filter",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

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