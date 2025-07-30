from .server import mcp


def main():
    """
    Main function to run the MCP server.
    """
    mcp.run(transport="stdio")
