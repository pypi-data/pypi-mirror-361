"""
Complete framework adapters for seamless integration
"""

import asyncio
import json
import inspect
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Union, Type
from abc import ABC, abstractmethod

from .client import HexaEightMCPClient, ToolResult

class BaseAdapter(ABC):
    """Base adapter for all framework integrations"""
    
    def __init__(self, mcp_client: HexaEightMCPClient):
        self.mcp_client = mcp_client
    
    @abstractmethod
    def get_tools(self) -> Any:
        """Get tools in framework-specific format"""
        pass

def _run_async_tool(coro):
    """Helper to run async tool in sync context"""
    try:
        # Check if we're already in an event loop
        loop = asyncio.get_running_loop()
        # If we're in a loop, use a thread pool to run the coroutine
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running loop, create a new one
        return asyncio.run(coro)

class AutogenAdapter(BaseAdapter):
    """Complete adapter for Microsoft Autogen framework"""
    
    def __init__(self, mcp_client: HexaEightMCPClient):
        super().__init__(mcp_client)
        self._autogen_tools = None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools formatted for Autogen"""
        if self._autogen_tools is None:
            self._autogen_tools = []
            for tool_name, tool_schema in self.mcp_client.get_available_tools().items():
                self._autogen_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_schema["description"],
                        "parameters": tool_schema["inputSchema"]
                    }
                })
        return self._autogen_tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute tool and return Autogen-compatible result"""
        result = await self.mcp_client.call_tool(tool_name, **kwargs)
        return json.dumps(result.to_dict(), indent=2)
    
    def create_autogen_agent(self, name: str, system_message: str, **autogen_kwargs):
        """Create an Autogen agent with HexaEight tools"""
        try:
            from autogen import ConversableAgent
        except ImportError:
            raise ImportError("autogen required: pip install pyautogen")
        
        class HexaEightAutogenAgent(ConversableAgent):
            def __init__(self, adapter, **kwargs):
                super().__init__(**kwargs)
                self.hexaeight_adapter = adapter
                self._register_hexaeight_tools()
            
            def _register_hexaeight_tools(self):
                """Register HexaEight tools with Autogen"""
                tools = self.hexaeight_adapter.get_tools()
                for tool in tools:
                    function_name = tool["function"]["name"]
                    
                    # Create wrapper function with proper closure
                    def create_tool_wrapper(tool_name):
                        def tool_wrapper(**tool_kwargs):
                            # Use sync version for Autogen
                            coro = self.hexaeight_adapter.execute_tool(tool_name, **tool_kwargs)
                            return _run_async_tool(coro)
                        return tool_wrapper
                    
                    # Register with Autogen
                    self.register_function(
                        function_schema=tool,
                        function=create_tool_wrapper(function_name)
                    )
        
        return HexaEightAutogenAgent(
            adapter=self,
            name=name,
            system_message=system_message,
            **autogen_kwargs
        )

class CrewAIAdapter(BaseAdapter):
    """Complete adapter for CrewAI framework"""
    
    def __init__(self, mcp_client: HexaEightMCPClient):
        super().__init__(mcp_client)
        self._crewai_tools = None
    
    def get_tools(self) -> List[Callable]:
        """Get tools formatted for CrewAI"""
        if self._crewai_tools is None:
            self._crewai_tools = []
            
            for tool_name, tool_schema in self.mcp_client.get_available_tools().items():
                def create_tool_function(name: str, schema: Dict[str, Any]):
                    def tool_function(**kwargs):
                        """CrewAI tool function (synchronous)"""
                        coro = self.mcp_client.call_tool(name, **kwargs)
                        result = _run_async_tool(coro)
                        return json.dumps(result.to_dict(), indent=2)
                    
                    tool_function.__name__ = name
                    tool_function.__doc__ = schema["description"]
                    return tool_function
                
                self._crewai_tools.append(create_tool_function(tool_name, tool_schema))
        
        return self._crewai_tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute tool and return CrewAI-compatible result"""
        result = await self.mcp_client.call_tool(tool_name, **kwargs)
        return result.to_dict()
    
    def create_crewai_agent(self, role: str, goal: str, backstory: str, **crewai_kwargs):
        """Create a CrewAI agent with HexaEight tools"""
        try:
            from crewai import Agent
        except ImportError:
            raise ImportError("crewai required: pip install crewai")
        
        # Get tools for CrewAI
        tools = self.get_tools()
        
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            **crewai_kwargs
        )

class LangChainAdapter(BaseAdapter):
    """Complete adapter for LangChain framework"""
    
    def __init__(self, mcp_client: HexaEightMCPClient):
        super().__init__(mcp_client)
        self._langchain_tools = None
    
    def get_tools(self) -> List[Any]:
        """Get tools formatted for LangChain"""
        try:
            from langchain.tools import BaseTool
            from pydantic import BaseModel, Field
        except ImportError:
            raise ImportError("langchain required: pip install langchain")
        
        if self._langchain_tools is None:
            self._langchain_tools = []
            
            for tool_name, tool_schema in self.mcp_client.get_available_tools().items():
                # Create Pydantic model for inputs
                fields = {}
                for prop_name, prop_def in tool_schema["inputSchema"].get("properties", {}).items():
                    field_type = str  # Default
                    if prop_def.get("type") == "integer":
                        field_type = int
                    elif prop_def.get("type") == "boolean":
                        field_type = bool
                    elif prop_def.get("type") == "array":
                        field_type = List[str]
                    
                    fields[prop_name] = (field_type, Field(description=prop_def.get("description", "")))
                
                InputModel = type(f"{tool_name}Input", (BaseModel,), fields)
                
                # Create tool class with proper closure
                def create_langchain_tool(name: str, schema: Dict[str, Any], input_model):
                    class HexaEightLangChainTool(BaseTool):
                        name: str = name
                        description: str = schema["description"]
                        args_schema: Type[BaseModel] = input_model
                        
                        def __init__(self, adapter):
                            super().__init__()
                            self.adapter = adapter
                            self.tool_name = name
                        
                        def _run(self, **kwargs) -> str:
                            """Synchronous execution"""
                            coro = self.adapter.execute_tool(self.tool_name, **kwargs)
                            result = _run_async_tool(coro)
                            return json.dumps(result, indent=2)
                        
                        async def _arun(self, **kwargs) -> str:
                            """Asynchronous execution"""
                            result = await self.adapter.execute_tool(self.tool_name, **kwargs)
                            return json.dumps(result, indent=2)
                    
                    return HexaEightLangChainTool
                
                tool_class = create_langchain_tool(tool_name, tool_schema, InputModel)
                self._langchain_tools.append(tool_class(self))
        
        return self._langchain_tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute tool and return LangChain-compatible result"""
        result = await self.mcp_client.call_tool(tool_name, **kwargs)
        return result.to_dict()

class GenericFrameworkAdapter(BaseAdapter):
    """Generic adapter for any framework - maximum flexibility"""
    
    def __init__(self, mcp_client: HexaEightMCPClient):
        super().__init__(mcp_client)
        self._generic_tools = None
        self._async_tools = None
    
    def get_tools(self) -> Dict[str, Callable]:
        """Get tools in generic callable format (synchronous)"""
        if self._generic_tools is None:
            self._generic_tools = {}
            
            for tool_name, tool_schema in self.mcp_client.get_available_tools().items():
                # Create sync wrapper with proper closure
                def create_sync_tool(name: str, schema: Dict[str, Any]):
                    def sync_tool(**kwargs):
                        coro = self.mcp_client.call_tool(name, **kwargs)
                        return _run_async_tool(coro)
                    
                    sync_tool.__name__ = name
                    sync_tool.__doc__ = schema["description"]
                    return sync_tool
                
                self._generic_tools[tool_name] = create_sync_tool(tool_name, tool_schema)
        
        return self._generic_tools
    
    def get_async_tools(self) -> Dict[str, Callable]:
        """Get tools in async callable format"""
        if self._async_tools is None:
            self._async_tools = {}
            
            for tool_name, tool_schema in self.mcp_client.get_available_tools().items():
                # Create async wrapper with proper closure
                def create_async_tool(name: str, schema: Dict[str, Any]):
                    async def async_tool(**kwargs):
                        return await self.mcp_client.call_tool(name, **kwargs)
                    
                    async_tool.__name__ = name
                    async_tool.__doc__ = schema["description"]
                    return async_tool
                
                self._async_tools[tool_name] = create_async_tool(tool_name, tool_schema)
        
        return self._async_tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute tool and return raw ToolResult"""
        return await self.mcp_client.call_tool(tool_name, **kwargs)
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool schemas for custom integration"""
        return self.mcp_client.get_available_tools()

class FrameworkDetector:
    """Utility to detect available frameworks and suggest adapters"""
    
    @staticmethod
    def detect_available_frameworks() -> Dict[str, bool]:
        """Detect which frameworks are available"""
        frameworks = {
            "autogen": False,
            "crewai": False, 
            "langchain": False,
            "semantic_kernel": False
        }
        
        # Test imports
        try:
            import autogen
            frameworks["autogen"] = True
        except ImportError:
            pass
        
        try:
            import crewai
            frameworks["crewai"] = True
        except ImportError:
            pass
        
        try:
            import langchain
            frameworks["langchain"] = True
        except ImportError:
            pass
        
        try:
            import semantic_kernel
            frameworks["semantic_kernel"] = True
        except ImportError:
            pass
        
        return frameworks
    
    @staticmethod
    def get_recommended_adapter(mcp_client: HexaEightMCPClient):
        """Get recommended adapter based on available frameworks"""
        available = FrameworkDetector.detect_available_frameworks()
        
        if available["autogen"]:
            return AutogenAdapter(mcp_client)
        elif available["crewai"]:
            return CrewAIAdapter(mcp_client)
        elif available["langchain"]:
            return LangChainAdapter(mcp_client)
        else:
            return GenericFrameworkAdapter(mcp_client)
    
    @staticmethod
    def print_framework_status():
        """Print status of available frameworks"""
        available = FrameworkDetector.detect_available_frameworks()
        
        print("🔍 Framework Detection Results:")
        print("=" * 35)
        
        for framework, is_available in available.items():
            status = "✅ Available" if is_available else "❌ Not installed"
            print(f"{framework.ljust(15)}: {status}")
        
        if not any(available.values()):
            print("\n📦 Install frameworks:")
            print("  pip install pyautogen    # Microsoft Autogen")
            print("  pip install crewai       # CrewAI")
            print("  pip install langchain    # LangChain")

def create_adapter_for_framework(framework_name: str, mcp_client: HexaEightMCPClient):
    """Factory function to create adapter for specific framework"""
    adapters = {
        "autogen": AutogenAdapter,
        "crewai": CrewAIAdapter,
        "langchain": LangChainAdapter,
        "generic": GenericFrameworkAdapter
    }
    
    if framework_name.lower() not in adapters:
        raise ValueError(f"Unsupported framework: {framework_name}")
    
    return adapters[framework_name.lower()](mcp_client)

def auto_detect_and_create_adapter(mcp_client: HexaEightMCPClient):
    """Automatically detect best framework and create adapter"""
    return FrameworkDetector.get_recommended_adapter(mcp_client)
