import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# 1. Initialisiere den puren MCP-Server (Kein Agenten-Framework!)
server = Server("pure-inference-tools")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Präsentiert der KI ihre direkt nutzbaren 'Hände' (Werkzeuge)."""
    return [
        types.Tool(
            name="read_memory",
            description="Liest die AI.md, um den aktuellen Projektstatus direkt in die Inferenz zu laden.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="update_memory",
            description="Überschreibt die AI.md mit der komprimierten Essenz der neuen Inferenz.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Der neue, komplett bereinigte Markdown-Inhalt."}
                },
                "required": ["content"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Führt das Tool ohne JSON-Umwege oder Agenten-Schleifen direkt aus."""
    if name == "read_memory":
        try:
            with open("AI.md", "r", encoding="utf-8") as f:
                return [types.TextContent(type="text", text=f.read())]
        except FileNotFoundError:
            return [types.TextContent(type="text", text="# AI Memory Bank\nInitialisiert.")]

    elif name == "update_memory":
        content = arguments.get("content", "")
        with open("AI.md", "w", encoding="utf-8") as f:
            f.write(content)
        return [types.TextContent(type="text", text="AI.md wurde erfolgreich aktualisiert und komprimiert.")]
    
    raise ValueError(f"Unbekanntes Tool: {name}")

async def main():
    # Starte den Server über Standard-I/O (Perfekt für VS Code / Gemini Integration)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pure-inference-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())