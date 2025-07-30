"""
OpenAI GPT LLM provider with function calling support for MCP tools
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from .base import LLMProvider

logger = logging.getLogger(__name__)

from openai import AsyncOpenAI
from dotenv import load_dotenv
        
load_dotenv()


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation using function calling for MCP tools"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: Optional API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to gpt-4.1)
        """
        
        # Configure API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        tools: List[Dict[str, Any]] = None,
        mcp_config: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using OpenAI API with function calling
        
        Args:
            messages: Conversation history
            tools: Tool definitions in standard format
            mcp_config: MCP configuration (not used for OpenAI)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dictionary with content, tool_calls, and raw_response
        """
        # Convert tools to OpenAI function format
        openai_tools = []
        if tools:
            for tool in tools:
                # Handle both direct tool format and nested function format
                if "function" in tool:
                    # Already in OpenAI format
                    openai_tools.append(tool)
                else:
                    # Convert from standard format to OpenAI format
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "parameters": tool.get("input_schema", tool.get("inputSchema", {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }))
                        }
                    }
                    openai_tools.append(openai_tool)
        
        # Extract generation parameters
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add tools if available
        if openai_tools:
            api_params["tools"] = openai_tools
            api_params["tool_choice"] = "auto"
        
        logger.debug(f"Calling OpenAI with model {self.model}")
        logger.debug(f"Tools provided: {len(openai_tools) if openai_tools else 0}")
        
        # Make API call
        try:
            response = await self.client.chat.completions.create(**api_params)
            
            # Extract message from response
            message = response.choices[0].message
            
            # Parse response
            result = {
                "content": message.content or "",
                "tool_calls": [],
                "raw_response": response
            }
            
            # Extract tool calls if present
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        mcp_config: Dict[str, Any] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming response using OpenAI API
        
        Note: Tool calling with streaming requires special handling
        """
        # For now, implement non-streaming version
        # OpenAI's streaming with tools requires accumulating chunks
        result = await self.generate(messages, tools, mcp_config, **kwargs)
        
        # Yield the complete response as a single chunk
        yield {
            "type": "content",
            "content": result["content"]
        }
        
        # Yield tool calls if any
        for tool_call in result.get("tool_calls", []):
            yield {
                "type": "tool_call",
                "tool_call": tool_call
            }