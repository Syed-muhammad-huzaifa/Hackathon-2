"""
MCP integration example with local stdio server.

This example demonstrates:
- MCPServerStdio setup
- Agent with MCP tools
- Async context manager usage
"""

import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def main():
    # Initialize MCP server as context manager
    async with MCPServerStdio(
        name="Task Server",
        params={
            "command": "python",
            "args": ["mcp_server.py"]  # Your MCP server script
        }
    ) as server:
        # Create agent with MCP server
        agent = Agent(
            name="Task Manager",
            instructions="You help users manage tasks using MCP tools.",
            mcp_servers=[server]
        )

        # Run agent
        result = await Runner.run(agent, "Add a task: Buy groceries")
        print(f"Response: {result.final_output}")

        # Another turn
        result = await Runner.run(agent, "List all my tasks")
        print(f"Response: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
