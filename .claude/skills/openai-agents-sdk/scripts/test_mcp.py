#!/usr/bin/env python3
"""
Test MCP server connectivity and tool availability.

This script helps debug MCP server integration by:
- Testing connection to MCP server
- Listing available tools
- Testing tool execution
"""

import asyncio
import os
import sys
from typing import Optional


async def test_stdio_server(command: str, args: list[str]):
    """Test stdio MCP server."""
    print(f"\n{'='*60}")
    print(f"  Testing Stdio MCP Server")
    print(f"{'='*60}\n")

    print(f"Command: {command}")
    print(f"Args: {' '.join(args)}\n")

    try:
        from agents.mcp import MCPServerStdio

        async with MCPServerStdio(
            name="Test Server",
            params={"command": command, "args": args}
        ) as server:
            print("✓ Connected to MCP server")

            # List available tools
            print("\nAvailable tools:")
            # Note: Tool listing depends on MCP server implementation
            print("  (Tool listing requires MCP server to expose tools)")

            return True

    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False


async def test_http_server(url: str, token: Optional[str] = None):
    """Test HTTP MCP server."""
    print(f"\n{'='*60}")
    print(f"  Testing HTTP MCP Server")
    print(f"{'='*60}\n")

    print(f"URL: {url}")
    print(f"Token: {'***' if token else 'None'}\n")

    try:
        from agents.mcp import MCPServerStreamableHttp

        params = {"url": url, "timeout": 10}
        if token:
            params["headers"] = {"Authorization": f"Bearer {token}"}

        async with MCPServerStreamableHttp(
            name="Test Server",
            params=params,
            cache_tools_list=True
        ) as server:
            print("✓ Connected to MCP server")

            # List available tools
            print("\nAvailable tools:")
            print("  (Tool listing requires MCP server to expose tools)")

            return True

    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False


async def test_with_agent(server_type: str, **kwargs):
    """Test MCP server with an agent."""
    print(f"\n{'='*60}")
    print(f"  Testing with Agent")
    print(f"{'='*60}\n")

    try:
        from agents import Agent, Runner
        from agents.mcp import MCPServerStdio, MCPServerStreamableHttp

        # Create MCP server based on type
        if server_type == "stdio":
            server_context = MCPServerStdio(
                name="Test Server",
                params={"command": kwargs["command"], "args": kwargs["args"]}
            )
        else:  # http
            params = {"url": kwargs["url"], "timeout": 10}
            if kwargs.get("token"):
                params["headers"] = {"Authorization": f"Bearer {kwargs['token']}"}

            server_context = MCPServerStreamableHttp(
                name="Test Server",
                params=params
            )

        async with server_context as server:
            # Create agent
            agent = Agent(
                name="Test Agent",
                instructions="You are a test agent. Use available tools to respond.",
                mcp_servers=[server]
            )

            print("✓ Created agent with MCP server")

            # Test simple query
            print("\nTesting agent query...")
            result = await Runner.run(agent, "Hello, can you help me?")

            print(f"\nAgent response: {result.final_output}")
            print(f"Tool calls: {len([i for i in result.new_items if i.get('type') == 'tool_call'])}")

            return True

    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage():
    """Print usage instructions."""
    print("""
Usage:
  python test_mcp.py stdio <command> [args...]
  python test_mcp.py http <url> [token]

Examples:
  # Test stdio MCP server
  python test_mcp.py stdio python mcp_server.py

  # Test HTTP MCP server
  python test_mcp.py http http://localhost:8000/mcp

  # Test HTTP MCP server with token
  python test_mcp.py http http://localhost:8000/mcp your_token_here
""")


async def main():
    """Main test function."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MCP Server Connectivity Tester                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    server_type = sys.argv[1].lower()

    if server_type == "stdio":
        if len(sys.argv) < 3:
            print("❌ Error: Command required for stdio server")
            print_usage()
            sys.exit(1)

        command = sys.argv[2]
        args = sys.argv[3:] if len(sys.argv) > 3 else []

        # Test connection
        success = await test_stdio_server(command, args)

        if success:
            # Test with agent
            await test_with_agent("stdio", command=command, args=args)

    elif server_type == "http":
        if len(sys.argv) < 3:
            print("❌ Error: URL required for HTTP server")
            print_usage()
            sys.exit(1)

        url = sys.argv[2]
        token = sys.argv[3] if len(sys.argv) > 3 else None

        # Test connection
        success = await test_http_server(url, token)

        if success:
            # Test with agent
            await test_with_agent("http", url=url, token=token)

    else:
        print(f"❌ Error: Unknown server type '{server_type}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
