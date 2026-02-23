#!/usr/bin/env python3
"""
Test MCP task server tools.

This script tests all 5 task management tools.
"""

import asyncio
import httpx
import json
import sys


BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user"


async def test_add_task():
    """Test add_task tool."""
    print("\n=== Testing add_task ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp/tools/add_task",
            json={
                "user_id": TEST_USER_ID,
                "title": "Test Task 1",
                "description": "This is a test task"
            }
        )

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if "task_id" in result:
            print("✓ Task created successfully")
            return result["task_id"]
        else:
            print("✗ Failed to create task")
            return None


async def test_list_tasks():
    """Test list_tasks tool."""
    print("\n=== Testing list_tasks ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp/tools/list_tasks",
            json={
                "user_id": TEST_USER_ID,
                "status": "all"
            }
        )

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if isinstance(result, list):
            print(f"✓ Found {len(result)} tasks")
        else:
            print("✗ Failed to list tasks")


async def test_complete_task(task_id: int):
    """Test complete_task tool."""
    print("\n=== Testing complete_task ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp/tools/complete_task",
            json={
                "user_id": TEST_USER_ID,
                "task_id": task_id
            }
        )

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("status") == "completed":
            print("✓ Task completed successfully")
        else:
            print("✗ Failed to complete task")


async def test_update_task(task_id: int):
    """Test update_task tool."""
    print("\n=== Testing update_task ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp/tools/update_task",
            json={
                "user_id": TEST_USER_ID,
                "task_id": task_id,
                "title": "Updated Test Task"
            }
        )

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("status") == "updated":
            print("✓ Task updated successfully")
        else:
            print("✗ Failed to update task")


async def test_delete_task(task_id: int):
    """Test delete_task tool."""
    print("\n=== Testing delete_task ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp/tools/delete_task",
            json={
                "user_id": TEST_USER_ID,
                "task_id": task_id
            }
        )

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("status") == "deleted":
            print("✓ Task deleted successfully")
        else:
            print("✗ Failed to delete task")


async def test_health():
    """Test health endpoint."""
    print("\n=== Testing health endpoint ===")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False


async def main():
    """Run all tests."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MCP Task Server Tool Tests                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    # Check if server is running
    if not await test_health():
        print("\n✗ Server is not running. Start the server first:")
        print("  python mcp_server.py")
        sys.exit(1)

    # Test all tools
    task_id = await test_add_task()

    if task_id:
        await test_list_tasks()
        await test_update_task(task_id)
        await test_complete_task(task_id)
        await test_list_tasks()
        await test_delete_task(task_id)
        await test_list_tasks()

    print("\n=== All tests completed ===\n")


if __name__ == "__main__":
    asyncio.run(main())
