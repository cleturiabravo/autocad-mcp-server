"""Example: drive the server over stdio with the MCP client, then (optionally)
hand the tool results to Claude.

    python example_usage.py path/to/drawing.dxf
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(path: str) -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "src.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])
            for name, args in [("read_dwg", {"path": path}),
                               ("list_layers", {}),
                               ("list_blocks", {})]:
                result = await session.call_tool(name, args)
                print(f"\n== {name} ==")
                for block in result.content:
                    print(block.text)

            # To use with Claude (anthropic SDK), convert the tools:
            #   [{"name": t.name, "description": t.description,
            #     "input_schema": t.inputSchema} for t in tools.tools]
            # and forward tool_use blocks to session.call_tool(name, input).
            _ = json  # keep import for users extending this example


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1]))
