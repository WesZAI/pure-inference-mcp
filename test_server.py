"""Tests for Pure Inference MCP Server."""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from main import server, MEMORY_FILE


@pytest.fixture
def temp_memory_file():
    """Create a temporary memory file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test Memory\nInitial content.")
        temp_path = f.name
    
    # Temporarily override the global MEMORY_FILE
    original = server._memory_file if hasattr(server, '_memory_file') else None
    
    yield temp_path
    
    # Cleanup
    if original:
        server._memory_file = original
    os.unlink(temp_path)


@pytest.mark.asyncio
async def test_list_tools():
    """Test that the server lists the expected tools."""
    tools = await server.handle_list_tools()
    
    assert len(tools) == 2
    
    tool_names = [tool.name for tool in tools]
    assert "read_memory" in tool_names
    assert "update_memory" in tool_names
    
    # Check read_memory tool
    read_tool = next(t for t in tools if t.name == "read_memory")
    assert "read" in read_tool.description.lower()
    assert read_tool.inputSchema["type"] == "object"
    
    # Check update_memory tool
    update_tool = next(t for t in tools if t.name == "update_memory")
    assert "update" in update_tool.description.lower()
    assert "content" in update_tool.inputSchema["properties"]


@pytest.mark.asyncio
async def test_read_memory_file_exists():
    """Test reading memory when file exists."""
    # Create a temporary AI.md
    test_content = "# Test Memory\nTest content."
    with open("AI.md", "w") as f:
        f.write(test_content)
    
    try:
        results = await server.handle_call_tool("read_memory", {})
        assert len(results) == 1
        assert results[0].type == "text"
        assert results[0].text == test_content
    finally:
        os.remove("AI.md")


@pytest.mark.asyncio
async def test_read_memory_file_not_exists():
    """Test reading memory when file doesn't exist."""
    # Remove AI.md if it exists
    if os.path.exists("AI.md"):
        os.remove("AI.md")
    
    results = await server.handle_call_tool("read_memory", {})
    assert len(results) == 1
    assert results[0].type == "text"
    assert "# AI Memory Bank" in results[0].text
    assert "Initialisiert" in results[0].text or "Initialized" in results[0].text


@pytest.mark.asyncio
async def test_update_memory():
    """Test updating memory with new content."""
    test_content = "# Updated Memory\nNew content."
    
    try:
        results = await server.handle_call_tool(
            "update_memory", 
            {"content": test_content}
        )
        assert len(results) == 1
        assert results[0].type == "text"
        assert "updated" in results[0].text.lower() or "erfolgreich" in results[0].text.lower()
        
        # Verify file was written
        with open("AI.md", "r") as f:
            assert f.read() == test_content
    finally:
        if os.path.exists("AI.md"):
            os.remove("AI.md")


@pytest.mark.asyncio
async def test_update_memory_empty_content():
    """Test updating memory with empty content."""
    results = await server.handle_call_tool("update_memory", {"content": ""})
    assert len(results) == 1
    # Should handle empty content gracefully
    assert results[0].type == "text"


@pytest.mark.asyncio
async def test_unknown_tool():
    """Test calling an unknown tool raises error."""
    with pytest.raises(ValueError, match="Unbekanntes Tool"):
        await server.handle_call_tool("unknown_tool", {})


@pytest.mark.asyncio
async def test_update_memory_missing_content():
    """Test updating memory without content parameter."""
    results = await server.handle_call_tool("update_memory", {})
    assert len(results) == 1
    assert results[0].type == "text"
    # Should return an error message
    assert "Error" in results[0].text or "Fehler" in results[0].text or "content" in results[0].text.lower()
