"""
Custom exceptions for HexaEight MCP Client
"""

class HexaEightMCPError(Exception):
    """Base exception for HexaEight MCP Client"""
    pass

class MCPConnectionError(HexaEightMCPError):
    """Raised when MCP server connection fails"""
    pass

class MCPToolError(HexaEightMCPError):
    """Raised when tool execution fails"""
    pass

class AgentCreationError(HexaEightMCPError):
    """Raised when agent creation fails"""
    pass

class DotnetScriptError(HexaEightMCPError):
    """Raised when dotnet script execution fails"""
    pass
