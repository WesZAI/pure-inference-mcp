import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MEMORY_FILE = os.getenv("AI_MEMORY_FILE", "AI.md")
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "pure-inference-tools")
SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")

server = Server(SERVER_NAME)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="read_memory",
            description="Read the AI.md file to load current project state.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="update_memory",
            description="Update the AI.md file with compressed project state.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The new markdown content for AI.md",
                        "minLength": 1
                    }
                },
                "required": ["content"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[dict]
) -> list[types.TextContent]:
    """Execute tools directly."""
    if name == "read_memory":
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return [types.TextContent(type="text", text=f.read())]
        except FileNotFoundError:
            logger.warning(f"Memory file {MEMORY_FILE} not found, returning default")
            return [types.TextContent(type="text", text="# AI Memory Bank\nInitialized.")]
        except Exception as e:
            logger.error(f"Error reading memory file: {e}")
            return [types.TextContent(type="text", text=f"Error reading memory: {str(e)}")]

    elif name == "update_memory":
        if not arguments or "content" not in arguments:
            return [types.TextContent(type="text", text="Error: content parameter is required")]

        content = arguments["content"]
        if not isinstance(content, str) or len(content.strip()) == 0:
            return [types.TextContent(type="text", text="Error: content must be a non-empty string")]

        try:
            # Backup existing file
            backup_path = f"{MEMORY_FILE}.bak"
            if Path(MEMORY_FILE).exists():
                Path(MEMORY_FILE).rename(backup_path)
                logger.info(f"Created backup at {backup_path}")

            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Updated memory file {MEMORY_FILE}")
            return [types.TextContent(type="text", text=f"AI.md updated successfully. Backup created at {backup_path}")]

        except Exception as e:
            logger.error(f"Error updating memory file: {e}")
            return [types.TextContent(type="text", text=f"Error updating memory: {str(e)}")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
