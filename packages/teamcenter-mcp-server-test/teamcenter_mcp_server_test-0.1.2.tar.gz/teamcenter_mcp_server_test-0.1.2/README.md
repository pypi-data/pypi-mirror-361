# Teamcenter MCP Server

Universal MCP server for integrating AI assistants with Teamcenter Knowledge Base APIs.

📦 **Live on PyPI:** https://pypi.org/project/teamcenter-mcp-server-test/

## Quick Start (Just Copy & Paste)

### Continue.dev
Add to `~/.continue/config.json`:
```json
{
  "experimental": {
    "modelContextProtocolServers": [{
      "transport": {
        "type": "stdio",
        "command": "uvx",
        "args": ["teamcenter-mcp-server-test", "--base-url", "http://localhost:8000"]
      }
    }]
  }
}
```

### VS Code
Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "teamcenter": {
      "type": "stdio",
      "command": "uvx",
      "args": ["teamcenter-mcp-server-test", "--base-url", "http://localhost:8000"]
    }
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
      "args": ["teamcenter-mcp-server-test", "--base-url", "http://localhost:8000"]
    }
  }
}
```

## Usage

**→ [See USAGE.md for copy & paste examples](USAGE.md) ←**

Quick examples:
- **VS Code**: `@workspace get Teamcenter API documentation for part creation`
- **Continue.dev**: `@MCP search for PLM workflow integration documentation`

## Production Setup

Replace `http://localhost:8000` with your real Teamcenter API:
```json
"args": ["teamcenter-mcp-server-test", "--base-url", "https://teamcenter.yourcompany.com"]
```

## Testing

### Quick Test
```bash
uvx teamcenter-mcp-server-test --version
```

### Demo/Development Setup

Start mock API server:
```bash
git clone https://github.com/your-repo/mock-api
cd mock-api
uv run uvicorn main:app --reload
```

Server runs on `http://localhost:8000` - use this URL in configs above.

---

## Development (Advanced)

<details>
<summary>Click for development setup</summary>

### Installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Build Package
```bash
uv build
```

### Run Tests
```bash
uv run pytest tests/ -v
```

### Publishing to PyPI
**→ [See DEVELOPER.md for release instructions](DEVELOPER.md) ←**

### Files Overview
- `auth_mcp_stdio.py`: Main MCP server
- `main.py`: Mock API server for development
- `pyproject.toml`: Package configuration

</details>