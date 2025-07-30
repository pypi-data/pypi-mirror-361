#!/usr/bin/env python3
"""MCP Calculator Server - stdio transport version."""

import sys
from mcp.server.fastmcp import FastMCP

def create_server() -> FastMCP:
    """Create and configure the MCP calculator server."""
    mcp = FastMCP(name="calculator-app")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers together.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
        """
        return a + b

    @mcp.tool()
    def subtract(a: int, b: int) -> int:
        """Subtract two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The difference of a and b
        """
        return a - b

    @mcp.tool()
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The product of a and b
        """
        return a * b

    @mcp.tool()
    def divide(a: float, b: float) -> float:
        """Divide two numbers.
        
        Args:
            a: First number (dividend)
            b: Second number (divisor)
            
        Returns:
            The quotient of a and b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    return mcp


def main():
    """Main entry point for the MCP calculator server."""
    # Default to stdio transport
    transport = "stdio"
    
    # Parse command line arguments for transport type
    if len(sys.argv) > 1:
        if "--transport" in sys.argv:
            transport_idx = sys.argv.index("--transport")
            if transport_idx + 1 < len(sys.argv):
                transport = sys.argv[transport_idx + 1]
    
    mcp = create_server()
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse", host="127.0.0.1", port=8060)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


if __name__ == "__main__":
    main() 