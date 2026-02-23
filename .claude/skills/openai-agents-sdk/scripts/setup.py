#!/usr/bin/env python3
"""
Setup script for OpenAI Agents SDK project.

This script helps initialize a new agent project with:
- Dependency installation
- Environment file creation
- Database initialization
- Configuration validation
"""

import os
import sys
import subprocess
from pathlib import Path


def print_step(message: str):
    """Print a step message."""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version is 3.11+."""
    print_step("Checking Python version")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current: {version.major}.{version.minor}")
        sys.exit(1)

    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")


def install_dependencies():
    """Install required dependencies."""
    print_step("Installing dependencies")

    requirements = [
        "openai-agents-sdk>=1.0.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "sqlmodel>=0.0.14",
        "python-dotenv>=1.0.0",
    ]

    print("Installing core dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + requirements,
            check=True,
            capture_output=True
        )
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def create_env_file():
    """Create .env file from template."""
    print_step("Creating environment file")

    if Path(".env").exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return

    env_content = """# OpenAI Agents SDK Environment Variables

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000/mcp
MCP_TOKEN=your_mcp_server_token_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
AGENT_SESSIONS_DB=agent_sessions.db

# Security
JWT_SECRET=your_jwt_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Agent Configuration
MAX_TURNS=10
REQUEST_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("✓ Created .env file")
    print("⚠️  Please update .env with your actual configuration")


def create_project_structure():
    """Create basic project structure."""
    print_step("Creating project structure")

    directories = [
        "app",
        "app/agents",
        "app/api",
        "tests",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        (Path(directory) / "__init__.py").touch()

    print("✓ Created project structure:")
    for directory in directories:
        print(f"  - {directory}/")


def create_main_file():
    """Create main.py template."""
    print_step("Creating main.py template")

    if Path("main.py").exists():
        print("main.py already exists, skipping")
        return

    main_content = '''"""
Main FastAPI application with OpenAI Agents SDK.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global agent

    logger.info("Starting application...")

    # TODO: Initialize your agent here
    # from agents import Agent
    # agent = Agent(name="Assistant", instructions="...")

    yield

    logger.info("Shutting down...")

app = FastAPI(
    title="Agent API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat(message: str):
    """Chat endpoint."""
    # TODO: Implement chat logic
    return {"response": "Not implemented yet"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

    with open("main.py", "w") as f:
        f.write(main_content)

    print("✓ Created main.py template")


def initialize_database():
    """Initialize SQLite database."""
    print_step("Initializing database")

    db_file = "agent_sessions.db"

    if Path(db_file).exists():
        print(f"✓ Database {db_file} already exists")
    else:
        # Create empty database file
        Path(db_file).touch()
        print(f"✓ Created database {db_file}")


def create_gitignore():
    """Create .gitignore file."""
    print_step("Creating .gitignore")

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

    print("✓ Created .gitignore")


def print_next_steps():
    """Print next steps for the user."""
    print_step("Setup Complete!")

    print("""
Next steps:

1. Update .env file with your configuration:
   - Add your OPENAI_API_KEY
   - Configure MCP_SERVER_URL if using MCP tools

2. Implement your agent in main.py:
   - Define agent with instructions
   - Add tools or MCP servers
   - Implement chat endpoint logic

3. Run the application:
   python main.py

4. Test the API:
   curl http://localhost:8000/health

For more information, see the OpenAI Agents SDK documentation.
""")


def main():
    """Main setup function."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     OpenAI Agents SDK Project Setup                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    try:
        check_python_version()
        install_dependencies()
        create_env_file()
        create_project_structure()
        create_main_file()
        initialize_database()
        create_gitignore()
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
