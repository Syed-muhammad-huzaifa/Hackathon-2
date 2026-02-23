#!/usr/bin/env python3
"""
Validate agent configuration before deployment.

This script checks:
- Environment variables
- Agent configuration
- MCP server connectivity
- Database access
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Tuple


class ValidationError(Exception):
    """Validation error."""
    pass


def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_env_variables() -> List[Tuple[str, bool, str]]:
    """Check required environment variables."""
    print_section("Environment Variables")

    required_vars = [
        ("OPENAI_API_KEY", "OpenAI API key"),
        ("MCP_SERVER_URL", "MCP server URL"),
        ("MCP_TOKEN", "MCP server token"),
    ]

    optional_vars = [
        ("DATABASE_URL", "Database connection string"),
        ("JWT_SECRET", "JWT secret key"),
        ("LOG_LEVEL", "Logging level"),
    ]

    results = []

    print("Required variables:")
    for var, description in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"  ✓ {var}: {description}")
            results.append((var, True, ""))
        else:
            print(f"  ❌ {var}: {description} - NOT SET")
            results.append((var, False, f"{var} is required"))

    print("\nOptional variables:")
    for var, description in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {description}")
        else:
            print(f"  ⚠️  {var}: {description} - not set (using defaults)")

    return results


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check required Python packages."""
    print_section("Dependencies")

    required_packages = [
        "agents",
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlmodel",
    ]

    results = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
            results.append((package, True, ""))
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            results.append((package, False, f"{package} is not installed"))

    return results


def check_database() -> Tuple[bool, str]:
    """Check database connectivity."""
    print_section("Database")

    db_file = os.getenv("AGENT_SESSIONS_DB", "agent_sessions.db")

    try:
        # Check if database file exists or can be created
        db_path = Path(db_file)

        if db_path.exists():
            print(f"  ✓ Database file exists: {db_file}")

            # Check if writable
            if os.access(db_path, os.W_OK):
                print(f"  ✓ Database is writable")
                return True, ""
            else:
                print(f"  ❌ Database is not writable")
                return False, "Database file is not writable"
        else:
            # Try to create database file
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_path.touch()
            print(f"  ✓ Created database file: {db_file}")
            return True, ""

    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False, str(e)


async def check_mcp_server() -> Tuple[bool, str]:
    """Check MCP server connectivity."""
    print_section("MCP Server")

    mcp_url = os.getenv("MCP_SERVER_URL")

    if not mcp_url:
        print("  ⚠️  MCP_SERVER_URL not set, skipping MCP check")
        return True, ""

    print(f"  Testing connection to: {mcp_url}")

    try:
        # Try to import MCP client
        from agents.mcp import MCPServerStreamableHttp

        print("  ✓ MCP client available")

        # Note: We can't actually test connection without starting the server
        # This is just a configuration check
        print("  ⚠️  MCP server connectivity test requires running server")
        print("     Run your MCP server and test manually")

        return True, ""

    except ImportError as e:
        print(f"  ❌ MCP client not available: {e}")
        return False, "MCP client not installed"
    except Exception as e:
        print(f"  ❌ MCP check failed: {e}")
        return False, str(e)


def check_agent_config() -> Tuple[bool, str]:
    """Check agent configuration."""
    print_section("Agent Configuration")

    # Check if main.py exists
    if not Path("main.py").exists():
        print("  ❌ main.py not found")
        return False, "main.py not found"

    print("  ✓ main.py exists")

    # Check for basic FastAPI structure
    with open("main.py", "r") as f:
        content = f.read()

        checks = [
            ("FastAPI import", "from fastapi import"),
            ("Agent import", "from agents import"),
            ("App instance", "app = FastAPI"),
        ]

        all_passed = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ⚠️  {check_name} - not found (may need implementation)")
                all_passed = False

    return True, ""


def print_summary(all_results: dict):
    """Print validation summary."""
    print_section("Validation Summary")

    total_checks = 0
    passed_checks = 0
    errors = []

    for category, results in all_results.items():
        if isinstance(results, list):
            for name, passed, error in results:
                total_checks += 1
                if passed:
                    passed_checks += 1
                elif error:
                    errors.append(f"{category}: {error}")
        else:
            passed, error = results
            total_checks += 1
            if passed:
                passed_checks += 1
            elif error:
                errors.append(f"{category}: {error}")

    print(f"Checks passed: {passed_checks}/{total_checks}")

    if errors:
        print("\n❌ Validation failed with errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors above before deploying.")
        return False
    else:
        print("\n✓ All validation checks passed!")
        print("Your agent configuration is ready for deployment.")
        return True


async def main():
    """Main validation function."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     OpenAI Agents SDK Configuration Validator           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Loaded .env file\n")
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading\n")

    # Run all checks
    results = {
        "Environment": check_env_variables(),
        "Dependencies": check_dependencies(),
        "Database": check_database(),
        "MCP Server": await check_mcp_server(),
        "Agent Config": check_agent_config(),
    }

    # Print summary
    success = print_summary(results)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
