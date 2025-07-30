"""
Base LLM provider interface
"""

from typing import List, Dict, Any, Protocol, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers to ensure compatibility"""
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, mcp_config: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            messages: Conversation history
            tools: Optional list of available tools
            mcp_config: Optional MCP server configuration for native MCP support
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Dict with 'content', 'tool_calls', and 'raw_response'
        """
        ...