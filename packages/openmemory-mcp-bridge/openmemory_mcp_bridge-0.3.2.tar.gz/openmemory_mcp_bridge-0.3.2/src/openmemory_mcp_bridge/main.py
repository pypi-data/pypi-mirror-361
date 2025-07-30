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
                        },
                        "memory": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of memories to add (alternative parameter name)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_memories",
                "description": "Get memories for a user with full filtering and pagination support. This method is called everytime before answering user queries to understand user's preferences and history.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "Filter by specific app ID (UUID format)"
                        },
                        "from_date": {
                            "type": "integer",
                            "description": "Filter memories created after this date (timestamp)"
                        },
                        "to_date": {
                            "type": "integer", 
                            "description": "Filter memories created before this date (timestamp)"
                        },
                        "categories": {
                            "type": "string",
                            "description": "Filter by categories (comma-separated)"
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Search query to filter memories"
                        },
                        "sort_column": {
                            "type": "string",
                            "description": "Column to sort by (memory, categories, app_name, created_at)",
                            "enum": ["memory", "categories", "app_name", "created_at"]
                        },
                        "sort_direction": {
                            "type": "string",
                            "description": "Sort direction",
                            "enum": ["asc", "desc"]
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "size": {
                            "type": "integer",
                            "description": "Page size (default: 50, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": []
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
                "name": "pause_memories",
                "description": "Pause memories based on various criteria (IDs, categories, app, or global).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of memory IDs to pause"
                        },
                        "category_ids": {
                            "type": "array",
                            "items": {"type": "string"}, 
                            "description": "List of category IDs to pause"
                        },
                        "app_id": {
                            "type": "string",
                            "description": "App ID to pause memories for"
                        },
                        "all_for_app": {
                            "type": "boolean",
                            "description": "Pause all memories for the specified app"
                        },
                        "global_pause": {
                            "type": "boolean",
                            "description": "Pause all memories globally"
                        },
                        "state": {
                            "type": "string",
                            "description": "New state to set",
                            "enum": ["active", "paused", "archived", "deleted"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_memory_access_log", 
                "description": "Get the access log for a specific memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The ID of the memory to get access log for"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Page size (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["memory_id"]
                }
            },
            {
                "name": "filter_memories",
                "description": "Advanced filtering of memories with complex criteria.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "app_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by app IDs"
                        },
                        "category_ids": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Filter by category IDs"
                        },
                        "sort_column": {
                            "type": "string",
                            "description": "Column to sort by"
                        },
                        "sort_direction": {
                            "type": "string",
                            "description": "Sort direction",
                            "enum": ["asc", "desc"]
                        },
                        "from_date": {
                            "type": "integer",
                            "description": "Filter memories created after this timestamp"
                        },
                        "to_date": {
                            "type": "integer",
                            "description": "Filter memories created before this timestamp"
                        },
                        "show_archived": {
                            "type": "boolean",
                            "description": "Include archived memories (default: false)"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "size": {
                            "type": "integer",
                            "description": "Page size (default: 50, max: 100)", 
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": []
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
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "size": {
                            "type": "integer",
                            "description": "Page size (default: 50, max: 100)",
                            "minimum": 1,
                            "maximum": 100
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
                "description": "List all apps associated with the user with full filtering and pagination.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Filter by app name"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Filter by active status"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort by field (default: name)"
                        },
                        "sort_direction": {
                            "type": "string",
                            "description": "Sort direction (default: asc)",
                            "enum": ["asc", "desc"]
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Page size (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_app_details",
                "description": "Get detailed information about a specific app.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "The ID of the app to get details for"
                        }
                    },
                    "required": ["app_id"]
                }
            },
            {
                "name": "update_app_details",
                "description": "Update app details (activate/deactivate).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "The ID of the app to update"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Set the active status of the app"
                        }
                    },
                    "required": ["app_id", "is_active"]
                }
            },
            {
                "name": "list_app_memories",
                "description": "List all memories for a specific app.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "The ID of the app to list memories for"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Page size (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["app_id"]
                }
            },
            {
                "name": "list_app_accessed_memories",
                "description": "List memories that have been accessed by a specific app.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "The ID of the app to list accessed memories for"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (default: 1)",
                            "minimum": 1
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Page size (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["app_id"]
                }
            },
            {
                "name": "get_configuration",
                "description": "Get the current OpenMemory configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_configuration",
                "description": "Update the OpenMemory configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "Configuration object to update",
                            "properties": {
                                "mem0": {
                                    "type": "object",
                                    "description": "Mem0 configuration"
                                },
                                "openmemory": {
                                    "type": "object", 
                                    "description": "OpenMemory specific configuration"
                                }
                            }
                        }
                    },
                    "required": ["config"]
                }
            },
            {
                "name": "reset_configuration",
                "description": "Reset the configuration to default values.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_llm_configuration",
                "description": "Get only the LLM configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_llm_configuration",
                "description": "Update only the LLM configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "llm_config": {
                            "type": "object",
                            "description": "LLM configuration object",
                            "properties": {
                                "provider": {
                                    "type": "string",
                                    "description": "LLM provider name"
                                },
                                "config": {
                                    "type": "object",
                                    "description": "Provider-specific configuration"
                                }
                            },
                            "required": ["provider", "config"]
                        }
                    },
                    "required": ["llm_config"]
                }
            },
            {
                "name": "get_embedder_configuration", 
                "description": "Get only the Embedder configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_embedder_configuration",
                "description": "Update only the Embedder configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "embedder_config": {
                            "type": "object",
                            "description": "Embedder configuration object",
                            "properties": {
                                "provider": {
                                    "type": "string",
                                    "description": "Embedder provider name"
                                },
                                "config": {
                                    "type": "object",
                                    "description": "Provider-specific configuration"
                                }
                            },
                            "required": ["provider", "config"]
                        }
                    },
                    "required": ["embedder_config"]
                }
            },
            {
                "name": "get_openmemory_configuration",
                "description": "Get only the OpenMemory configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_openmemory_configuration",
                "description": "Update only the OpenMemory configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "openmemory_config": {
                            "type": "object",
                            "description": "OpenMemory configuration object",
                            "properties": {
                                "custom_instructions": {
                                    "type": "string",
                                    "description": "Custom instructions for memory management"
                                }
                            }
                        }
                    },
                    "required": ["openmemory_config"]
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
            elif tool_name == "get_memory_by_id":
                result = await self._get_memory_by_id(arguments)
            elif tool_name == "update_memory":
                result = await self._update_memory(arguments)
            elif tool_name == "get_categories":
                result = await self._get_categories(arguments)
            elif tool_name == "archive_memories":
                result = await self._archive_memories(arguments)
            elif tool_name == "pause_memories":
                result = await self._pause_memories(arguments)
            elif tool_name == "get_memory_access_log":
                result = await self._get_memory_access_log(arguments)
            elif tool_name == "filter_memories":
                result = await self._filter_memories(arguments)
            elif tool_name == "get_related_memories":
                result = await self._get_related_memories(arguments)
            elif tool_name == "get_user_stats":
                result = await self._get_user_stats(arguments)
            elif tool_name == "list_apps":
                result = await self._list_apps(arguments)
            elif tool_name == "get_app_details":
                result = await self._get_app_details(arguments)
            elif tool_name == "update_app_details":
                result = await self._update_app_details(arguments)
            elif tool_name == "list_app_memories":
                result = await self._list_app_memories(arguments)
            elif tool_name == "list_app_accessed_memories":
                result = await self._list_app_accessed_memories(arguments)
            elif tool_name == "get_configuration":
                result = await self._get_configuration(arguments)
            elif tool_name == "update_configuration":
                result = await self._update_configuration(arguments)
            elif tool_name == "reset_configuration":
                result = await self._reset_configuration(arguments)
            elif tool_name == "get_llm_configuration":
                result = await self._get_llm_configuration(arguments)
            elif tool_name == "update_llm_configuration":
                result = await self._update_llm_configuration(arguments)
            elif tool_name == "get_embedder_configuration":
                result = await self._get_embedder_configuration(arguments)
            elif tool_name == "update_embedder_configuration":
                result = await self._update_embedder_configuration(arguments)
            elif tool_name == "get_openmemory_configuration":
                result = await self._get_openmemory_configuration(arguments)
            elif tool_name == "update_openmemory_configuration":
                result = await self._update_openmemory_configuration(arguments)
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
        # Handle both "memories" (plural) and "memory" (singular) for compatibility
        memories = arguments.get("memories", arguments.get("memory", []))
        
        # OpenMemory API expects individual memory creation calls
        results = []
        logger.info(f"Adding {len(memories)} memories for user {self.user_id} via app {self.client}")
        
        for i, memory_text in enumerate(memories):
            payload = {
                "user_id": self.user_id,
                "text": memory_text,
                "infer": False,
                "app": self.client
            }
            
            logger.info(f"Memory {i+1}/{len(memories)}: {memory_text[:100]}...")
            logger.info(f"Payload: {payload}")
            
            try:
                response = await self.http_client.post(
                    f"{self.base_url}/api/v1/memories/",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"API Response Status: {response.status_code}")
                logger.info(f"API Response Text: {response.text}")
                response.raise_for_status()
                result = response.json()
                results.append(result)
                logger.info(f"Memory {i+1} added successfully: {result}")
            except Exception as e:
                logger.error(f"Failed to add memory {i+1}: {e}")
                results.append({"error": str(e), "memory_text": memory_text})
        
        logger.info(f"Final results: {results}")
        return {"results": results, "count": len(results)}

    async def _get_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memories from OpenMemory"""
        app_id = arguments.get("app_id")
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        categories = arguments.get("categories")
        search_query = arguments.get("search_query")
        sort_column = arguments.get("sort_column", "created_at")
        sort_direction = arguments.get("sort_direction", "desc")
        page = arguments.get("page", 1)
        size = arguments.get("size", 50)

        params = {
            "user_id": self.user_id,
            "page": page,
            "size": size,
            "sort_column": sort_column,
            "sort_direction": sort_direction
        }

        if app_id:
            params["app_id"] = app_id
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if categories:
            params["categories"] = categories
        if search_query:
            params["search_query"] = search_query

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/memories/",
            params=params
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
        memories_response = await self._get_memories({"app_id": "", "page": 1, "size": 50}) # Get all memories for the user
        
        if "items" in memories_response:
            memory_ids = [memory["id"] for memory in memories_response["items"]]
            
            if memory_ids:
                # Delete all memories using the regular delete endpoint
                return await self._delete_memories({"memory_ids": memory_ids})
            else:
                return {"message": "No memories found to delete", "count": 0}
        else:
            return {"message": "No memories found to delete", "count": 0}

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
        
        params = {
            "user_id": self.user_id
        }
        
        # The API expects an array of memory IDs in the body
        payload = memory_ids
        
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/actions/archive",
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _pause_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Pause memories based on various criteria"""
        memory_ids = arguments.get("memory_ids", [])
        category_ids = arguments.get("category_ids", [])
        app_id = arguments.get("app_id")
        all_for_app = arguments.get("all_for_app", False)
        global_pause = arguments.get("global_pause", False)
        state = arguments.get("state", "paused") # Default to "paused"

        payload = {
            "memory_ids": memory_ids,
            "category_ids": category_ids,
            "app_id": app_id,
            "all_for_app": all_for_app,
            "global_pause": global_pause,
            "state": state,
            "user_id": self.user_id
        }

        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/actions/pause",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_memory_access_log(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory access log for a specific memory"""
        memory_id = arguments.get("memory_id")
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)

        params = {
            "page": page,
            "page_size": page_size
        }

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/memories/{memory_id}/access-log",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _filter_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced filtering of memories"""
        search_query = arguments.get("search_query")
        app_ids = arguments.get("app_ids", [])
        category_ids = arguments.get("category_ids", [])
        sort_column = arguments.get("sort_column")
        sort_direction = arguments.get("sort_direction", "desc")
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        show_archived = arguments.get("show_archived", False)
        page = arguments.get("page", 1)
        size = arguments.get("size", 50)

        params = {
            "page": page,
            "size": size
        }

        payload = {
            "user_id": self.user_id,
            "page": page,
            "size": size,
            "show_archived": show_archived
        }

        if search_query:
            payload["search_query"] = search_query
        if app_ids:
            payload["app_ids"] = app_ids
        if category_ids:
            payload["category_ids"] = category_ids
        if sort_column:
            payload["sort_column"] = sort_column
        if sort_direction:
            payload["sort_direction"] = sort_direction
        if from_date:
            payload["from_date"] = from_date
        if to_date:
            payload["to_date"] = to_date

        response = await self.http_client.post(
            f"{self.base_url}/api/v1/memories/filter",
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_related_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get related memories for a specific memory"""
        memory_id = arguments.get("memory_id")
        page = arguments.get("page", 1)
        size = arguments.get("size", 50)
        
        params = {
            "user_id": self.user_id,
            "page": page,
            "size": size
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
        name = arguments.get("name")
        is_active = arguments.get("is_active")
        sort_by = arguments.get("sort_by", "name")
        sort_direction = arguments.get("sort_direction", "asc")
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)

        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_direction": sort_direction
        }

        if name:
            params["name"] = name
        if is_active is not None:
            params["is_active"] = is_active

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/apps/",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _get_app_details(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific app"""
        app_id = arguments.get("app_id")

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/apps/{app_id}",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_app_details(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update app details (activate/deactivate)"""
        app_id = arguments.get("app_id")
        is_active = arguments.get("is_active")

        params = {
            "is_active": is_active
        }

        response = await self.http_client.put(
            f"{self.base_url}/api/v1/apps/{app_id}",
            params=params,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _list_app_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all memories for a specific app"""
        app_id = arguments.get("app_id")
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)

        params = {
            "page": page,
            "page_size": page_size
        }

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/apps/{app_id}/memories",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _list_app_accessed_memories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List memories that have been accessed by a specific app"""
        app_id = arguments.get("app_id")
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)

        params = {
            "page": page,
            "page_size": page_size
        }

        response = await self.http_client.get(
            f"{self.base_url}/api/v1/apps/{app_id}/accessed",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def _get_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current OpenMemory configuration"""
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/config/",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update the OpenMemory configuration"""
        config = arguments.get("config")

        response = await self.http_client.put(
            f"{self.base_url}/api/v1/config/",
            json=config,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _reset_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Reset the configuration to default values"""
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/config/reset",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_llm_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get only the LLM configuration"""
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/config/mem0/llm",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_llm_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update only the LLM configuration"""
        llm_config = arguments.get("llm_config")

        response = await self.http_client.put(
            f"{self.base_url}/api/v1/config/mem0/llm",
            json=llm_config,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_embedder_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get only the Embedder configuration"""
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/config/mem0/embedder",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_embedder_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update only the Embedder configuration"""
        embedder_config = arguments.get("embedder_config")

        response = await self.http_client.put(
            f"{self.base_url}/api/v1/config/mem0/embedder",
            json=embedder_config,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _get_openmemory_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get only the OpenMemory configuration"""
        response = await self.http_client.get(
            f"{self.base_url}/api/v1/config/openmemory",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def _update_openmemory_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update only the OpenMemory configuration"""
        openmemory_config = arguments.get("openmemory_config")

        response = await self.http_client.put(
            f"{self.base_url}/api/v1/config/openmemory",
            json=openmemory_config,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        # Handle notifications (no id field) - these don't need responses
        if request_id is None:
            if method == "notifications/initialized":
                logger.info("Client initialized notification received")
                return None
            else:
                logger.info(f"Unknown notification: {method}")
                return None
        
        # Handle regular requests (with id field) - these need responses
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
            "id": request_id,
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
                    
                    # Only send response if one was generated (not for notifications)
                    if response is not None:
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
                    
                    # Only send error response for requests (with id), not for notifications
                    if 'request' in locals() and request.get("id") is not None:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
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