# Teamcenter MCP Server

A complete solution for integrating AI assistants with Teamcenter Knowledge Base APIs. Includes both a mock API server for development and a deployable MCP server for production use.

## What You Get

- **Mock API Server**: Test server that simulates Teamcenter Knowledge Base responses
- **MCP Server**: Production-ready server that connects AI assistants to Teamcenter APIs
- **Universal Deployment**: Works across all IDEs and platforms via UVX

## Quick Start

### 1. Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Start Mock API Server
```bash
# Start the mock API server (for development/testing)
uv run uvicorn main:app --reload
```
Server runs on `http://127.0.0.1:8000`

### 3. Build MCP Server Package
```bash
# Build the deployable MCP server
uv build
```
Creates: `dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl`

### 4. Validate Your Setup
```bash
# Run the deployment validation test
python test_mcp_contract.py
```
This validates that your UVX wheel deployment is ready for IDE integration.

## Deployment Options

### Option 1: UVX (Recommended - Universal)

**Use the built wheel package anywhere:**
```bash
# From the built wheel (works on any machine)
uvx --from dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl teamcenter-mcp-server --base-url http://localhost:8000
```

**Why UVX is better:**
- ✅ **No virtual environment conflicts** (Windows/WSL compatible)
- ✅ **Works anywhere** (just copy the .whl file)
- ✅ **No installation required** (isolated execution)

### Option 2: Direct Python (Development Only)

**Run directly from source:**
```bash
# For development/testing only
uv run python auth_mcp_stdio.py --base-url http://localhost:8000
```

## IDE Integration

### VS Code
Update `.vscode/mcp.json`:
```json
{
  "servers": {
    "teamcenter": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "http://localhost:8000"]
    }
  }
}
```

### Continue.dev
Update `~/.continue/config.json`:
```json
{
  "experimental": {
    "modelContextProtocolServers": [{
      "transport": {
        "type": "stdio",
        "command": "uvx",
        "args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "http://localhost:8000"]
      }
    }]
  }
}
```

### JetBrains IDEs
Add to `~/.mcp.json`:
```json
{
  "mcpServers": {
    "teamcenter": {
      "command": "uvx",
      "args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "http://localhost:8000"]
    }
  }
}
```

## Testing

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Validate Setup
```bash
# Pre-flight check - run this before configuring IDEs
python test_mcp_contract.py
```

**What this tests:**
- ✅ UVX wheel package works
- ✅ MCP server initializes correctly
- ✅ Command-line arguments work
- ✅ API server connectivity (optional)

**Run this whenever you:**
- Build a new wheel (`uv build`)
- Change server configurations
- Set up on a new machine

## 🚀 Production Deployment

**Ready to connect to your real Teamcenter API?** Replace the mock server with your production endpoint:

### Replace Mock URL with Production
```bash
# Instead of: --base-url http://localhost:8000
# Use your real Teamcenter API:
--base-url https://teamcenter.yourcompany.com
```

### Update IDE Configurations
**VS Code** (`.vscode/mcp.json`):
```json
"args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "https://teamcenter.yourcompany.com"]
```

**Continue.dev** (`~/.continue/config.json`):
```json
"args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "https://teamcenter.yourcompany.com"]
```

### Alternative: Environment Variable
```bash
# Set once, works everywhere
export TEAMCENTER_API_URL=https://teamcenter.yourcompany.com

# Then use without --base-url:
"args": ["--from", "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server"]
```

**🎯 That's it! No mock server needed - connect directly to production.**

## Usage Examples

Once configured, ask your AI assistant:

- `@MCP check if the Teamcenter knowledge base is healthy`
- `@MCP search for PLM workflow integration documentation`
- `@MCP find CAD model versioning guides`

## Files Overview

- **`auth_mcp_stdio.py`**: Main MCP server (single file solution)
- **`main.py`**: Mock API server for development
- **`test_mcp_contract.py`**: Deployment validation script
- **`pyproject.toml`**: Package configuration for `uv build`
- **`dist/`**: Built wheel packages (created by `uv build`)

## Key Commands

| Command | Purpose |
|---------|---------|
| `uv run uvicorn main:app --reload` | Start mock API server |
| `uv build` | Build MCP server package |
| `python test_mcp_contract.py` | **Validate setup (run first!)** |
| `uv run pytest tests/ -v` | Run all tests |
