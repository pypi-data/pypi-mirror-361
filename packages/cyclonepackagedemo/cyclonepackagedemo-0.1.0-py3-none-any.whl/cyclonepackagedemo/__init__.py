from mcp.server.fastmcp import FastMCP

# create mcp server
mcp = FastMCP("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b


mcp.resource("greeting://{name}")


def get_greeting(name: str) -> str:
    """get a personallized greeting"""
    return f"Hello, {name}!"


def main() -> None:
    mcp.server.host = "0.0.0.0"
    mcp.run(transport="stdio")
