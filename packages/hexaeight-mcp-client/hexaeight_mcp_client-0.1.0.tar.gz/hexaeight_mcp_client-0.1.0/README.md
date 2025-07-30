# HexaEight MCP Client

Framework-agnostic MCP (Model Context Protocol) client integration for HexaEight agents.

## Features

- 🔐 **Secure Identity Management** - Leverage HexaEight's identity and authentication
- 🤝 **Multi-Agent Communication** - Secure messaging via HexaEight PubSub
- 🛠️ **Framework Agnostic** - Works with Autogen, CrewAI, LangChain, and custom frameworks
- 🔧 **Agent Creation** - Create agents via integrated dotnet scripts
- ⚡ **Easy Setup** - Simple installation and quick start

## Installation

```bash
# Basic installation
pip install hexaeight-mcp-client

# With framework support
pip install hexaeight-mcp-client[autogen]    # For Autogen
pip install hexaeight-mcp-client[crewai]     # For CrewAI  
pip install hexaeight-mcp-client[langchain]  # For LangChain
pip install hexaeight-mcp-client[all]        # All frameworks
```

## Prerequisites

You need the core HexaEight agent package:

```bash
pip install hexaeight-agent
```

## Quick Start

### 1. Create HexaEight Agents

```python
from hexaeight_mcp_client import HexaEightAgentManager

# Create agent manager
manager = HexaEightAgentManager()

# Create parent agent
result = manager.create_parent_agent("my_parent.json")
print(f"Parent agent created: {result.success}")

# Create child agent
result = manager.create_child_agent("child_01", "my_parent.json", "my_child.json")
print(f"Child agent created: {result.success}")
```

### 2. Use MCP Client

```python
from hexaeight_mcp_client import HexaEightMCPClient

# Initialize client
client = HexaEightMCPClient()

# Load agent
await client.load_agent("my_parent.json", agent_type="parent")

# Connect to PubSub
await client.connect_to_pubsub("http://localhost:5000")

# Use tools
result = await client.call_tool("hexaeight_get_identity")
print("Agent identity:", result.content)

# Send secure message
result = await client.call_tool("hexaeight_send_message",
    pubsub_url="http://localhost:5000",
    target_type="agent_name",
    target_value="other_agent",
    message="Hello secure world!"
)
```

## Framework Integration

### Autogen

```python
from hexaeight_mcp_client import AutogenAdapter

adapter = AutogenAdapter(client)
autogen_agent = adapter.create_autogen_agent(
    name="SecureAgent",
    system_message="You have secure identity and communication tools"
)
```

### CrewAI

```python
from hexaeight_mcp_client import CrewAIAdapter

adapter = CrewAIAdapter(client)
crew_agent = adapter.create_crewai_agent(
    role="Secure Coordinator",
    goal="Coordinate tasks with secure identity",
    backstory="Expert in secure multi-agent coordination"
)
```

### LangChain

```python
from hexaeight_mcp_client import LangChainAdapter

adapter = LangChainAdapter(client)
langchain_tools = adapter.get_tools()
```

### Any Framework (Generic)

```python
from hexaeight_mcp_client import GenericFrameworkAdapter

adapter = GenericFrameworkAdapter(client)
tools = adapter.get_tools()

# Use any tool
result = tools["hexaeight_get_identity"]()
```

## Available Tools

- `hexaeight_get_identity` - Get agent identity and capabilities
- `hexaeight_send_message` - Send secure messages via PubSub
- `hexaeight_create_task` - Create and assign multi-step tasks
- `hexaeight_create_child_agent` - Create new child agents

## Requirements

- Python 3.8+
- hexaeight-agent package
- .NET SDK (for agent creation)

## License

MIT License - see LICENSE file for details.

## Links

- **Documentation**: [GitHub Repository](https://github.com/hexaeight/mcp-client)
- **Issues**: [GitHub Issues](https://github.com/hexaeight/mcp-client/issues)
- **HexaEight Agent**: [hexaeight-agent on PyPI](https://pypi.org/project/hexaeight-agent/)
