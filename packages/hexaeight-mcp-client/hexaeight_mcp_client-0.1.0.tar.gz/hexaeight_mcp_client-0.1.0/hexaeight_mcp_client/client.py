"""
HexaEight MCP Client - Complete implementation
Framework-agnostic MCP integration for HexaEight agents
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field

try:
    from hexaeight_agent import HexaEightAgent
except ImportError:
    raise ImportError("hexaeight-agent is required. Install with: pip install hexaeight-agent")

from .exceptions import HexaEightMCPError, MCPToolError

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized tool execution result"""
    success: bool
    content: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }
    
    def __str__(self) -> str:
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status}: {self.content if self.success else self.error}"

class HexaEightMCPClient:
    """
    Complete MCP client for HexaEight agents
    Framework-agnostic design for maximum compatibility
    """
    
    def __init__(self, hexaeight_agent: Optional[HexaEightAgent] = None):
        self.hexaeight_agent = hexaeight_agent
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self._initialized = False
        
        # Initialize built-in HexaEight tools
        self._register_hexaeight_tools()
    
    def _register_hexaeight_tools(self):
        """Register built-in HexaEight identity and communication tools"""
        hexaeight_tools = {
            "hexaeight_get_identity": {
                "name": "hexaeight_get_identity",
                "description": "Get HexaEight agent identity and capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "hexaeight_send_message": {
                "name": "hexaeight_send_message", 
                "description": "Send secure message via HexaEight PubSub",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pubsub_url": {"type": "string", "description": "PubSub server URL"},
                        "target_type": {"type": "string", "description": "Target type (agent_name/internal_id)"},
                        "target_value": {"type": "string", "description": "Target identifier"},
                        "message": {"type": "string", "description": "Message content"},
                        "message_type": {"type": "string", "default": "text", "description": "Message type"}
                    },
                    "required": ["pubsub_url", "target_type", "target_value", "message"]
                }
            },
            "hexaeight_create_task": {
                "name": "hexaeight_create_task",
                "description": "Create and assign multi-step task to agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pubsub_url": {"type": "string", "description": "PubSub server URL"},
                        "title": {"type": "string", "description": "Task title"},
                        "steps": {"type": "array", "items": {"type": "string"}, "description": "Task steps"},
                        "target_type": {"type": "string", "description": "Target type"},
                        "target_value": {"type": "string", "description": "Target identifier"}
                    },
                    "required": ["pubsub_url", "title", "steps", "target_type", "target_value"]
                }
            },
            "hexaeight_create_child_agent": {
                "name": "hexaeight_create_child_agent",
                "description": "Create new child agent with secure identity",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "agent_password": {"type": "string", "description": "Complex password for child agent"},
                        "config_filename": {"type": "string", "description": "Config file name"},
                        "client_id": {"type": "string", "description": "Client ID (optional)"},
                        "token_server_url": {"type": "string", "description": "Token server URL (optional)"}
                    },
                    "required": ["agent_password", "config_filename"]
                }
            }
        }
        
        self.available_tools.update(hexaeight_tools)
        
        # Register handlers
        self.tool_handlers["hexaeight_get_identity"] = self._handle_get_identity
        self.tool_handlers["hexaeight_send_message"] = self._handle_send_message  
        self.tool_handlers["hexaeight_create_task"] = self._handle_create_task
        self.tool_handlers["hexaeight_create_child_agent"] = self._handle_create_child_agent
    
    async def _handle_get_identity(self, **kwargs) -> ToolResult:
        """Handle get identity tool"""
        start_time = time.time()
        try:
            if not self.hexaeight_agent:
                return ToolResult(
                    False, None, "No HexaEight agent available",
                    execution_time=time.time() - start_time
                )
            
            agent_name = await self.hexaeight_agent.get_agent_name()
            internal_id = self.hexaeight_agent.get_internal_identity()
            
            identity_info = {
                "agent_name": agent_name,
                "internal_id": internal_id[:20] + "..." if len(internal_id) > 20 else internal_id,
                "is_connected_to_pubsub": self.hexaeight_agent.is_connected_to_pubsub(),
                "capabilities": {
                    "can_send_messages": True,
                    "can_create_tasks": True, 
                    "can_create_child_agents": True,
                    "has_secure_identity": bool(internal_id)
                }
            }
            
            return ToolResult(
                True, identity_info,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                False, None, str(e),
                execution_time=time.time() - start_time
            )
    
    async def _handle_send_message(self, **kwargs) -> ToolResult:
        """Handle send message tool"""
        start_time = time.time()
        try:
            if not self.hexaeight_agent:
                return ToolResult(
                    False, None, "No HexaEight agent available",
                    execution_time=time.time() - start_time
                )
            
            result = await self.hexaeight_agent.send_message(
                kwargs["pubsub_url"],
                kwargs["target_type"], 
                kwargs["target_value"],
                kwargs["message"],
                kwargs.get("message_type", "text")
            )
            
            return ToolResult(
                result,
                {
                    "message_sent": result, 
                    "target": f"{kwargs['target_type']}:{kwargs['target_value']}",
                    "message_length": len(kwargs["message"])
                },
                None if result else "Failed to send message",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                False, None, str(e),
                execution_time=time.time() - start_time
            )
    
    async def _handle_create_task(self, **kwargs) -> ToolResult:
        """Handle create task tool"""
        start_time = time.time()
        try:
            if not self.hexaeight_agent:
                return ToolResult(
                    False, None, "No HexaEight agent available",
                    execution_time=time.time() - start_time
                )
            
            result = await self.hexaeight_agent.create_task(
                kwargs["pubsub_url"],
                kwargs["title"],
                kwargs["steps"], 
                kwargs["target_type"],
                kwargs["target_value"]
            )
            
            return ToolResult(
                result,
                {
                    "task_created": result,
                    "title": kwargs["title"],
                    "steps_count": len(kwargs["steps"]),
                    "assigned_to": f"{kwargs['target_type']}:{kwargs['target_value']}"
                },
                None if result else "Failed to create task",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                False, None, str(e),
                execution_time=time.time() - start_time
            )
    
    async def _handle_create_child_agent(self, **kwargs) -> ToolResult:
        """Handle create child agent tool"""
        start_time = time.time()
        try:
            if not self.hexaeight_agent:
                return ToolResult(
                    False, None, "No HexaEight agent available",
                    execution_time=time.time() - start_time
                )
            
            result = self.hexaeight_agent.create_ai_child_agent(
                kwargs["agent_password"],
                kwargs["config_filename"],
                True,  # loadenv
                kwargs.get("client_id", ""),
                kwargs.get("token_server_url", "")
            )
            
            return ToolResult(
                result,
                {
                    "child_agent_created": result,
                    "config_file": kwargs["config_filename"] if result else None
                },
                None if result else "Failed to create child agent",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                False, None, str(e),
                execution_time=time.time() - start_time
            )
    
    async def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Call any available tool (HexaEight or external)"""
        if tool_name not in self.tool_handlers:
            return ToolResult(False, None, f"Tool {tool_name} not found")
        
        try:
            return await self.tool_handlers[tool_name](**kwargs)
        except Exception as e:
            return ToolResult(False, None, f"Tool execution error: {e}")
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tools"""
        return self.available_tools.copy()
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool"""
        return self.available_tools.get(tool_name)
    
    def list_tool_names(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self.available_tools.keys())
    
    async def load_agent(self, config_file: str, agent_type: str = "parent", agent_password: Optional[str] = None) -> bool:
        """
        Load HexaEight agent from config file
        
        Args:
            config_file: Path to agent config JSON file
            agent_type: "parent" or "child"
            agent_password: Required for child agents
            
        Returns:
            True if agent loaded successfully
        """
        try:
            if not self.hexaeight_agent:
                self.hexaeight_agent = HexaEightAgent()
            
            if agent_type == "parent":
                success = self.hexaeight_agent.load_ai_parent_agent(config_file, True)
            else:
                if not agent_password:
                    raise ValueError("Child agents require agent_password")
                success = self.hexaeight_agent.load_ai_child_agent(
                    agent_password, config_file, True
                )
            
            if success:
                logger.info(f"✅ Loaded {agent_type} agent from {config_file}")
            else:
                logger.error(f"❌ Failed to load {agent_type} agent from {config_file}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error loading agent: {e}")
            return False
    
    async def connect_to_pubsub(self, pubsub_url: str, agent_type: str = "child") -> bool:
        """Connect agent to PubSub server"""
        try:
            if not self.hexaeight_agent:
                raise ValueError("No agent loaded. Call load_agent() first.")
            
            success = await self.hexaeight_agent.connect_to_pubsub(pubsub_url, agent_type)
            
            if success:
                logger.info(f"✅ Connected to PubSub: {pubsub_url}")
            else:
                logger.error(f"❌ Failed to connect to PubSub: {pubsub_url}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error connecting to PubSub: {e}")
            return False
    
    def validate_tool_arguments(self, tool_name: str, **kwargs) -> List[str]:
        """Validate tool arguments against schema"""
        errors = []
        
        if tool_name not in self.available_tools:
            return [f"Tool {tool_name} not found"]
        
        schema = self.available_tools[tool_name].get("inputSchema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Check required arguments
        for req_arg in required:
            if req_arg not in kwargs:
                errors.append(f"Missing required argument: {req_arg}")
        
        # Basic type checking
        for arg_name, arg_value in kwargs.items():
            if arg_name in properties:
                prop = properties[arg_name]
                expected_type = prop.get("type")
                
                if expected_type == "string" and not isinstance(arg_value, str):
                    errors.append(f"Argument {arg_name} should be string")
                elif expected_type == "array" and not isinstance(arg_value, list):
                    errors.append(f"Argument {arg_name} should be array")
        
        return errors
