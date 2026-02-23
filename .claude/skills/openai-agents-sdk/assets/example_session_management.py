"""
Session management example with conversation persistence.

This example demonstrates:
- SQLiteSession usage
- Multi-turn conversations
- Context preservation
"""

import asyncio
from agents import Agent, Runner, SQLiteSession

async def main():
    # Create agent
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant. Remember context from previous messages."
    )

    # Create persistent session
    session = SQLiteSession("user_123", "conversations.db")

    print("=== Multi-Turn Conversation ===\n")

    # Turn 1
    print("User: My name is Alice and I live in Seattle.")
    result = await Runner.run(
        agent,
        "My name is Alice and I live in Seattle.",
        session=session
    )
    print(f"Assistant: {result.final_output}\n")

    # Turn 2 - agent remembers context
    print("User: What's my name?")
    result = await Runner.run(
        agent,
        "What's my name?",
        session=session
    )
    print(f"Assistant: {result.final_output}\n")

    # Turn 3 - agent still remembers
    print("User: Where do I live?")
    result = await Runner.run(
        agent,
        "Where do I live?",
        session=session
    )
    print(f"Assistant: {result.final_output}\n")

if __name__ == "__main__":
    asyncio.run(main())
