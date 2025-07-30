"""
Tools for Jay MCP server
"""

from mcp.server.fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """
    Register all tools with the MCP server
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def add(a: int, b: int) -> int:
        """
        Add two numbers
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of the two numbers plus 1000
        """
        return a + b + 1000
    
    @mcp.tool()
    def multiply(a: int, b: int) -> int:
        """
        Multiply two numbers
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of the two numbers
        """
        return a * b
    
    @mcp.tool()
    def get_info() -> dict:
        """
        Get server information
        
        Returns:
            Dictionary containing server information
        """
        return {
            "name": "Jay MCP Demo",
            "version": "0.1.0",
            "description": "A demo MCP server with tools and resources",
            "tools": ["add", "multiply", "get_info"],
            "resources": ["greeting"]
        }
