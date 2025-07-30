"""
Anthropic Claude LLM provider
"""

import os
import json
from typing import List, Dict, Any, Optional
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        from dotenv import load_dotenv
        
        load_dotenv()
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
    
    async def generate(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, mcp_config: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate response using Anthropic API with native MCP support"""
        # Extract parameters
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Convert to Anthropic format
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Use native MCP if config provided
        if mcp_config:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                mcp_servers=[mcp_config],
                extra_headers={
                    "anthropic-beta": "mcp-client-2025-04-04"
                }
            )
        # Fallback to standard tool calling
        elif tools:
            # Convert tools to Anthropic format
            anthropic_tools = []
            for tool in tools:
                anthropic_tools.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("inputSchema", {"type": "object", "properties": {}})
                })
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                tools=anthropic_tools,
                temperature=temperature
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                temperature=temperature
            )
        
        # Extract content and tool calls
        content = ""
        if hasattr(response, 'content') and response.content:
            if isinstance(response.content, list):
                for item in response.content:
                    if hasattr(item, 'text'):
                        content += item.text
            else:
                content = str(response.content)
        
        return {
            "content": content,
            "raw_response": response
        }