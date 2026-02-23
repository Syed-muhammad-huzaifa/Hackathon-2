# Scripts

Utility scripts for OpenAI Agents SDK projects.

---

## setup.py

Initialize a new OpenAI Agents SDK project.

**Usage:**
```bash
python scripts/setup.py
```

**What it does:**
- Checks Python version (3.11+ required)
- Installs core dependencies
- Creates .env file from template
- Creates project structure (app/, tests/)
- Creates main.py template
- Initializes SQLite database
- Creates .gitignore

**When to use:**
- Starting a new agent project
- Setting up development environment

---

## validate.py

Validate agent configuration before deployment.

**Usage:**
```bash
python scripts/validate.py
```

**What it checks:**
- Environment variables (OPENAI_API_KEY, MCP_SERVER_URL, etc.)
- Python dependencies installed
- Database connectivity
- MCP server configuration
- Agent configuration in main.py

**When to use:**
- Before deploying to production
- After configuration changes
- Troubleshooting setup issues

---

## test_mcp.py

Test MCP server connectivity and tool availability.

**Usage:**
```bash
# Test stdio MCP server
python scripts/test_mcp.py stdio python mcp_server.py

# Test HTTP MCP server
python scripts/test_mcp.py http http://localhost:8000/mcp

# Test HTTP MCP server with authentication
python scripts/test_mcp.py http http://localhost:8000/mcp your_token_here
```

**What it does:**
- Tests connection to MCP server
- Lists available tools (if supported)
- Creates test agent with MCP server
- Runs test query through agent

**When to use:**
- Debugging MCP server integration
- Verifying MCP server is running
- Testing tool availability
- Troubleshooting connection issues

---

## Quick Start

1. **Setup new project:**
   ```bash
   python scripts/setup.py
   ```

2. **Configure environment:**
   ```bash
   # Edit .env file with your configuration
   nano .env
   ```

3. **Validate configuration:**
   ```bash
   python scripts/validate.py
   ```

4. **Test MCP server (if using):**
   ```bash
   python scripts/test_mcp.py http http://localhost:8000/mcp
   ```

5. **Run application:**
   ```bash
   python main.py
   ```

---

## Troubleshooting

### "Module not found" errors
Run setup.py to install dependencies:
```bash
python scripts/setup.py
```

### MCP connection failures
1. Verify MCP server is running
2. Check MCP_SERVER_URL in .env
3. Test with test_mcp.py script

### Database errors
1. Check AGENT_SESSIONS_DB path in .env
2. Verify write permissions
3. Run validate.py to check database

### Environment variable issues
1. Ensure .env file exists
2. Check all required variables are set
3. Run validate.py to verify configuration
