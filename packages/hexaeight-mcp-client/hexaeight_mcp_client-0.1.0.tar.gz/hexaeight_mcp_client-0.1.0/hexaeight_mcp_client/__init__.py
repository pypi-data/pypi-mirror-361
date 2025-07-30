"""
HexaEight MCP Client
Framework-agnostic MCP integration for HexaEight agents
"""

__version__ = "0.1.0"
__author__ = "HexaEight"
__license__ = "MIT"

# Core exports
from .client import HexaEightMCPClient, ToolResult
from .agent_manager import HexaEightAgentManager
from .adapters import (
    AutogenAdapter,
    CrewAIAdapter, 
    LangChainAdapter,
    GenericFrameworkAdapter,
    FrameworkDetector
)
from .exceptions import HexaEightMCPError, MCPConnectionError, MCPToolError

__all__ = [
    "HexaEightMCPClient",
    "ToolResult",
    "HexaEightAgentManager",
    "AutogenAdapter",
    "CrewAIAdapter",
    "LangChainAdapter", 
    "GenericFrameworkAdapter",
    "FrameworkDetector",
    "HexaEightMCPError",
    "MCPConnectionError", 
    "MCPToolError"
]

def get_version():
    """Get package version"""
    return __version__

def check_requirements():
    """Check if required dependencies are available"""
    try:
        import hexaeight_agent
        return True, f"hexaeight-agent available: {getattr(hexaeight_agent, '__version__', 'unknown')}"
    except ImportError:
        return False, "hexaeight-agent required: pip install hexaeight-agent"
