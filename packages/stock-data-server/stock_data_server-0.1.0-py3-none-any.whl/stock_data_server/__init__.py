from .stock_data import mcp

def main() -> None:
    """
    Entry point for the stock-data-server package. Runs the MCP server using FastMCP.
    See MCP PyPI documentation for details: https://pypi.org/project/fastmcp/
    """
    mcp.run()
