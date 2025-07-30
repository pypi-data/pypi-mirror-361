"""
Observee Agents - A Python SDK for MCP tool integration with LLM providers
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv

from .agents.agent import MCPAgent

# Load environment variables
load_dotenv()

__version__ = "0.0.1"
__all__ = ["chat_with_tools", "MCPAgent"]


def _get_observee_config(
    observee_url: Optional[str] = None, 
    observee_api_key: Optional[str] = None,
    client_id: Optional[str] = None
):
    """
    Get Observee configuration with priority: params > env vars
    
    Args:
        observee_url: Direct URL (if provided, client_id will be replaced/added)
        observee_api_key: API key for authentication
        client_id: Client ID (from params or env var)
    
    Returns:
        dict: Configuration with 'url' and optional 'auth_token'
    
    Raises:
        ValueError: If no configuration is provided
    """
    # Get client_id with priority: param > env var
    if not client_id:
        client_id = os.getenv("OBSERVEE_CLIENT_ID")
    
    def _update_client_id_in_url(url: str, new_client_id: str) -> str:
        """Replace or add client_id in URL"""
        import re
        
        # If client_id already exists, replace it
        if "client_id=" in url:
            # Replace existing client_id value
            url = re.sub(r'client_id=[^&]*', f'client_id={new_client_id}', url)
        else:
            # Add client_id to URL if we have a client_id
            if new_client_id:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}client_id={new_client_id}"
        
        return url
    
    # Priority 1: Direct URL parameter
    if observee_url:
        if client_id:
            updated_url = _update_client_id_in_url(observee_url, client_id)
        else:
            updated_url = observee_url
        return {
            "url": updated_url,
            "auth_token": None
        }
    
    # Priority 2: API key parameter
    if observee_api_key:
        if not client_id:
            raise ValueError("client_id is required when using observee_api_key. Set OBSERVEE_CLIENT_ID env var or pass client_id parameter.")
        
        url = f"https://mcp.observee.ai/mcp?client_id={client_id}"
        return {
            "url": url,
            "auth_token": observee_api_key
        }
    
    # Priority 3: Environment variables
    env_url = os.getenv("OBSERVEE_URL")
    if env_url:
        if client_id:
            updated_url = _update_client_id_in_url(env_url, client_id)
        else:
            updated_url = env_url
        return {
            "url": updated_url,
            "auth_token": None
        }
    
    env_api_key = os.getenv("OBSERVEE_API_KEY")
    if env_api_key:
        if not client_id:
            raise ValueError("client_id is required when using OBSERVEE_API_KEY. Set OBSERVEE_CLIENT_ID env var or pass client_id parameter.")
        
        url = f"https://mcp.observee.ai/mcp?client_id={client_id}"
        return {
            "url": url,
            "auth_token": env_api_key
        }
    
    # No configuration provided
    raise ValueError(
        "No Observee configuration found. Please provide one of:\n"
        "1. observee_url parameter or OBSERVEE_URL env var\n"
        "2. observee_api_key parameter or OBSERVEE_API_KEY env var (requires client_id)\n"
        "3. Set environment variables in .env file"
    )

async def _chat_with_tools_async(
    message: str,
    provider: str = "anthropic",
    model: Optional[str] = None,
    observee_url: Optional[str] = None,
    observee_api_key: Optional[str] = None,
    client_id: Optional[str] = None,
    server_name: str = "observee",
    max_tools: int = 20,
    min_score: float = 8.0,
    filter_type: str = "bm25",
    enable_filtering: bool = True,
    sync_tools: bool = False,
    **provider_kwargs
) -> Dict[str, Any]:
    """
    Internal async function to handle the actual chat with tools logic
    """
    # Get configuration
    config = _get_observee_config(observee_url, observee_api_key, client_id)
    
    # Create and use agent with async context manager (like main.py/simpletest.py)
    async with MCPAgent(
        provider=provider,
        model=model,
        server_name=server_name,
        server_url=config["url"],
        auth_token=config["auth_token"],
        sync_tools=sync_tools,
        filter_type=filter_type,
        enable_filtering=enable_filtering,
        **provider_kwargs
    ) as agent:
        # Execute the chat with tools
        result = await agent.chat_with_tools(
            message=message,
            max_tools=max_tools,
            min_score=min_score
        )
        
        return result

def chat_with_tools(
    message: str,
    provider: str = "anthropic",
    model: Optional[str] = None,
    observee_url: Optional[str] = None,
    observee_api_key: Optional[str] = None,
    client_id: Optional[str] = None,
    server_name: str = "observee",
    max_tools: int = 20,
    min_score: float = 8.0,
    filter_type: str = "bm25",
    enable_filtering: bool = True,
    sync_tools: bool = False,
    **provider_kwargs
) -> Dict[str, Any]:
    """
    Synchronous wrapper for chat_with_tools that uses asyncio.run() internally.
    
    Args:
        message: The user message/query
        provider: LLM provider ("anthropic", "openai", "gemini")
        model: Model name (auto-detected if not provided)
        observee_url: Direct Observee URL (client_id will be appended if missing)
        observee_api_key: Observee API key for authentication
        client_id: Observee client ID (defaults to env var)
        server_name: MCP server name (default: "observee")
        max_tools: Maximum number of tools to filter (default: 20)
        min_score: Minimum relevance score for tool filtering (default: 8.0)
        filter_type: Tool filter type ("bm25", "local_embedding", "cloud")
        enable_filtering: Whether to enable tool filtering (default: True)
        sync_tools: Whether to clear caches and sync tools (default: False)
        **provider_kwargs: Additional arguments for the LLM provider
    
    Returns:
        Dict containing:
        - content: The response text
        - tool_calls: List of tool calls made
        - tool_results: Results from tool executions
        - filtered_tools_count: Number of tools after filtering
        - filtered_tools: List of filtered tool names
        - used_filtering: Whether filtering was used
    
    Example:
        ```python
        from observee_agents import chat_with_tools
        
        result = chat_with_tools(
            message="Search for recent news about AI",
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            observee_api_key="obs_your_key_here"
        )
        print(result["content"])
        ```
    """
    return asyncio.run(_chat_with_tools_async(
        message=message,
        provider=provider,
        model=model,
        observee_url=observee_url,
        observee_api_key=observee_api_key,
        client_id=client_id,
        server_name=server_name,
        max_tools=max_tools,
        min_score=min_score,
        filter_type=filter_type,
        enable_filtering=enable_filtering,
        sync_tools=sync_tools,
        **provider_kwargs
    ))
