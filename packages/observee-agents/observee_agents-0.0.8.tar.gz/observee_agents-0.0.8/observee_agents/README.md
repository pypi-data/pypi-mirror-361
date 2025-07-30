# Observee Agents

A powerful Python SDK for integrating Model Context Protocol (MCP) tools with multiple LLM providers (Anthropic Claude, OpenAI GPT, Google Gemini) and intelligent tool filtering.

MIT Licence version and open source of this toolkit coming soon.
## Features

- **Multi-Provider Support**: Works with Anthropic Claude, OpenAI GPT, and Google Gemini
- **Intelligent Tool Filtering**: BM25, local embedding, and cloud-based semantic search
- **Caching**: Automatic caching for improved performance
- **Flexible Authentication**: Support for URL and API key authentication methods
- **OAuth Integration**: Built-in authentication flows for Gmail, Slack, Notion, and 15+ services
- **Native MCP Support**: Optimized performance with Anthropic's native MCP when filtering is disabled

## Quick Start

### Installation

```bash
pip install observee-agents
```

### Configuration

**You must provide your own MCP server configuration.** Set up environment variables in a `.env` file:

```bash
# Option 1: Direct URL (already contains authentication)
OBSERVEE_URL=wss://mcp.observee.ai/mcp?customer_id=customer_id&client_id=your_client_id

# Option 2: API Key + Client ID  
OBSERVEE_API_KEY=your_api_key
OBSERVEE_CLIENT_ID=your_client_id or as a parameter

# LLM Provider API Keys (choose the provider you want to use)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key  
GOOGLE_API_KEY=your_gemini_key
```

### Basic Usage

```python
from observee_agents import chat_with_tools

# Simple synchronous usage (default)
result = chat_with_tools(
    "Search YouTube for Python tutorials",
    provider="anthropic"  # or "openai", "gemini"
)

print(f"Response: {result['content']}")
print(f"Tools used: {len(result.get('tool_calls', []))}")
```

### OAuth Authentication

The SDK includes built-in OAuth flows for authenticating with various services:

```python
from observee_agents import call_mcpauth_login, get_available_servers

# Get list of supported authentication servers
servers = get_available_servers()
print(f"Available servers: {servers['supported_servers']}")

# Start authentication flow for Gmail
response = call_mcpauth_login(auth_server="gmail")
print(f"Visit this URL to authenticate: {response['url']}")

# Start authentication flow for Slack with client ID
response = call_mcpauth_login(
    auth_server="slack"
)
```

**Supported Services**: Gmail, Google Calendar, Google Docs, Google Drive, Google Sheets, Slack, Notion, Linear, Asana, Outlook, OneDrive, Atlassian, Supabase, Airtable, Discord, and more.

### Async Usage

```python
import asyncio
from observee_agents import MCPAgent

async def main():
    # Async version using MCPAgent for better performance
    async with MCPAgent(
        provider="anthropic",
        server_url="wss://mcp.observee.ai/mcp?client_id=your_id",
        auth_token="your_api_key"
    ) as agent:
        result = await agent.chat_with_tools(
            "Search YouTube for Python tutorials"
        )
        
        print(f"Response: {result['content']}")
        print(f"Tools used: {len(result.get('tool_calls', []))}")

asyncio.run(main())
```

### Advanced Usage

```python
from observee_agents import chat_with_tools

# Advanced configuration with custom parameters (sync)
result = chat_with_tools(
    "Find recent videos about machine learning",
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    observee_url="wss://mcp.observee.ai/mcp?client_id=your_id",
    observee_api_key="your_api_key",  # Optional if URL contains auth
    client_id="your_client_id",       # Optional override
    filter_type="local_embedding",    # More semantic filtering
    sync_tools=True,                  # Sync tools to cloud storage
    enable_filtering=True             # Use filtered tools vs native MCP
)

print(f"Filtered tools: {result['filtered_tools_count']}")
print(f"Response: {result['content']}")
```

## Sync vs Async Usage

### Default Synchronous API
The default `chat_with_tools()` function is synchronous and perfect for:
- Scripts and simple applications
- Jupyter notebooks 
- Traditional non-async Python code

```python
from observee_agents import chat_with_tools

# Works in any synchronous context
result = chat_with_tools("Search for Python tutorials")
```

### Async API for Performance
Use `MCPAgent` when you're already in an async context:

```python
import asyncio
from observee_agents import MCPAgent

async def my_async_function():
    # Use this in async contexts for better performance
    async with MCPAgent(
        provider="anthropic",
        server_url="wss://mcp.observee.ai/mcp?client_id=your_id"
    ) as agent:
        result = await agent.chat_with_tools("Search for Python tutorials")
        return result
```

### Important: Context Detection
The sync version works in both sync and async contexts:

```python
async def example():
    # ✅ This works correctly - sync function can be called from async
    result = chat_with_tools("query")  
    
async def async_example():
    # ✅ This also works correctly for better async performance
    async with MCPAgent(provider="anthropic") as agent:
        result = await agent.chat_with_tools("query")
```

## Configuration Priority

The system uses the following priority for configuration:

1. **Function parameters** (highest priority)
2. **Environment variables** from `.env` file  
3. **Error if no configuration found** (no defaults provided)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OBSERVEE_URL` | Direct WebSocket URL with authentication | If not using API key |
| `OBSERVEE_API_KEY` | API key for authentication | If not using direct URL |
| `OBSERVEE_CLIENT_ID` | Client ID for MCP server | When using API key |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude models |
| `OPENAI_API_KEY` | OpenAI API key | For GPT models |
| `GOOGLE_API_KEY` | Google API key | For Gemini models |

## URL Handling

The system intelligently handles URL construction:

- **Direct URL**: Uses provided URL as-is, with optional client_id replacement
- **API key**: Constructs `https://mcp.observee.ai/mcp?client_id=...` with Bearer token auth
- **Client ID replacement**: Automatically replaces existing client_id parameters in URLs

## Filter Types

### BM25 Filter (Default)
- **Speed**: ~1-5ms
- **Type**: Keyword-based search
- **Cache**: `.bm25_index_cache.pkl`
- **Best for**: Exact keyword matches

### Local Embedding Filter  
- **Speed**: ~10ms
- **Type**: Semantic similarity search
- **Cache**: `.tool_embeddings_cache.pkl`
- **Best for**: Semantic understanding

### Cloud Filter
- **Speed**: ~300-400ms  
- **Type**: Hybrid search with Pinecone
- **Cache**: Remote vector store
- **Best for**: Large-scale semantic search

## Tool Filtering vs Native MCP

### With Filtering (`enable_filtering=True`)
- Uses tool filtering algorithms
- Works with all providers
- Reduces tool count based on query relevance
- Slightly slower due to filtering overhead

### Without Filtering (`enable_filtering=False`)  
- Uses provider's native MCP support when available
- Anthropic: Native MCP with `?beta=true` header
- OpenAI/Gemini: Standard tool conversion (no native MCP)
- Faster performance, all tools available

## Error Handling

The system provides clear error messages for common issues:

```python
# Missing configuration
ValueError: No Observee configuration found. Please provide one of:
1. observee_url parameter or OBSERVEE_URL env var
2. observee_api_key parameter or OBSERVEE_API_KEY env var (requires client_id)
3. Set environment variables in .env file

# Missing client ID with API key
ValueError: client_id is required when using observee_api_key. 
Set OBSERVEE_CLIENT_ID env var or pass client_id parameter.
```

## Examples

See `example_sdk.py` for complete usage examples with all providers and filter types.

## Command Line Usage

You can also run the system from command line:

```bash
# Basic usage (requires environment variables)
python main.py

# With specific provider and model
python main.py --provider openai --model gpt-4o

# With custom URL
python main.py --url "wss://mcp.observee.ai/mcp?client_id=your_id"

# With different filter types
python main.py --filter local_embedding --sync

# Disable filtering (use native MCP)
python main.py --no-filter
```

## License

MIT License