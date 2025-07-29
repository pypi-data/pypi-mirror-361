# ActValue Lambda MCP Server

A Python library for creating MCP (Model Context Protocol) servers that run on AWS Lambda.

## Installation

```bash
pip install actvalue.lambda-mcp-server
```

## Quick Start

```python
from lambda_mcp import LambdaMCPServer

# Create a server instance
server = LambdaMCPServer(
    name="my-mcp-server",
    version="1.0.0",
    instructions="A sample MCP server running on Lambda"
)

# Register tools using the decorator
@server.tool()
def hello_world(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

# Lambda handler
def lambda_handler(event, context):
    return server.handle_request(event, context)
```

## Features

- **AWS Lambda Integration**: Designed specifically for serverless deployment
- **Session Management**: Built-in Redis-based session storage
- **Tool Registration**: Easy decorator-based tool registration
- **MCP Protocol**: Full MCP protocol compliance
- **Type Safety**: Complete type annotations for better development experience

## Configuration

### Basic Configuration

```python
server = LambdaMCPServer(
    name="my-server",
    version="1.0.0",
    instructions="Server description",
    cache_prefix="my_sessions",  # Redis key prefix
    redis_url="redis://localhost:6379/0"
)
```

### Environment Variables

- `REDIS_URL`: Redis connection URL
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Session Management

Access and modify session data within your tools:

```python
@server.tool()
def store_data(key: str, value: str) -> str:
    session = server.get_session()
    if session:
        session.data[key] = value
        return f"Stored {key} = {value}"
    return "No active session"

@server.tool()
def get_data(key: str) -> str:
    session = server.get_session()
    if session and key in session.data:
        return str(session.data[key])
    return "Key not found"
```

## Develpment and test

### Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### Install package in development mode
```bash
pip install -e .
```

See examples and their README.md file.