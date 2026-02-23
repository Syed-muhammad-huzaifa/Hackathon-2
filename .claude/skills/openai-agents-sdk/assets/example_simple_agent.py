"""
Simple agent example with function tools.

This example demonstrates:
- Basic agent definition
- Function tools
- Sync and async execution
"""

from agents import Agent, Runner, function_tool
import asyncio

# Define function tools
@function_tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@function_tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

# Create agent
agent = Agent(
    name="Math Assistant",
    instructions="You help users with math calculations. Use the provided tools to perform calculations.",
    tools=[add_numbers, multiply_numbers]
)

# Async execution
async def async_example():
    print("=== Async Example ===")
    result = await Runner.run(agent, "What is 5 + 3?")
    print(f"Response: {result.final_output}")

# Sync execution
def sync_example():
    print("\n=== Sync Example ===")
    result = Runner.run_sync(agent, "What is 4 * 7?")
    print(f"Response: {result.final_output}")

if __name__ == "__main__":
    # Run async example
    asyncio.run(async_example())

    # Run sync example
    sync_example()
