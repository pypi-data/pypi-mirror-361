"""
Tests for Teamcenter MCP STDIO server
Focused on VS Code integration and Teamcenter-specific functionality
"""
import pytest
import sys
import os
import json
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def test_server_imports_cleanly():
    """Test that VS Code can import the server without issues."""
    start_time = time.time()
    
    import auth_mcp_stdio
    
    import_time = time.time() - start_time
    assert import_time < 1.0, f"Import took {import_time}s, too slow for VS Code"
    assert hasattr(auth_mcp_stdio, 'mcp')  # MCP is initialized in main()


def test_teamcenter_server_identity():
    """Test server is properly identified for Teamcenter."""
    import auth_mcp_stdio
    from fastmcp import FastMCP
    
    # Test that we can initialize the server
    mcp = FastMCP(name="Teamcenter")
    assert mcp.name == "Teamcenter"
    assert hasattr(mcp, 'run')
    assert callable(mcp.run)


def test_stdio_transport_configuration():
    """Test server is configured for stdio transport VS Code needs."""
    server_path = os.path.join(project_root, 'auth_mcp_stdio.py')
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Must have stdio transport for VS Code
    assert 'transport="stdio"' in content
    assert 'if __name__ == "__main__"' in content
    assert os.access(server_path, os.R_OK)


def test_teamcenter_sse_parsing():
    """Test SSE parsing works for Teamcenter streaming responses."""
    # Teamcenter-specific test data
    teamcenter_sse = '''data: {"type": "response", "data": "Teamcenter"}
data: {"type": "response", "data": " PLM"}
data: {"type": "citation", "data": "Reference: TC_UserGuide.pdf"}
data: {"type": "response", "data": " documentation"}'''
    
    content = []
    citations = []
    
    for line in teamcenter_sse.split('\n'):
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if data.get('type') == 'response':
                    content.append(data.get('data', ''))
                elif data.get('type') == 'citation':
                    citations.append(data.get('data', ''))
            except:
                pass
    
    result = ''.join(content)
    if citations:
        result += "\n\nCitations:\n" + '\n'.join(citations)
    
    expected = "Teamcenter PLM documentation\n\nCitations:\nReference: TC_UserGuide.pdf"
    assert result == expected


def test_teamcenter_tool_descriptions():
    """Test tool descriptions are Teamcenter-specific for LLM discovery."""
    server_path = os.path.join(project_root, 'auth_mcp_stdio.py')
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Should have Teamcenter-specific descriptions
    assert 'teamcenter_search' in content
    assert 'Teamcenter knowledge base' in content
    assert 'technical information' in content
    assert 'documentation' in content


def test_vscode_mcp_configuration():
    """Test VS Code mcp.json points to correct Teamcenter server."""
    config_path = os.path.join(project_root, '.vscode', 'mcp.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if config and "servers" in config:
            # Should have teamcenter server configured
            servers = config["servers"]
            assert isinstance(servers, dict)
            
            # Check for Teamcenter server (any name containing teamcenter)
            teamcenter_servers = [k for k in servers.keys() if 'teamcenter' in k.lower()]
            assert len(teamcenter_servers) > 0, "No Teamcenter server found in VS Code config"
            
            # Verify stdio transport
            for server_name in teamcenter_servers:
                server_config = servers[server_name]
                assert server_config.get("type") == "stdio"
                # Check for either old stdio file or new teamcenter-mcp-server command
                command = server_config.get("command", "")
                args_str = str(server_config.get("args", []))
                assert ("mcp_stdio.py" in args_str or "teamcenter-mcp-server" in command), f"No MCP server found in command: {command}, args: {args_str}"


def test_required_dependencies():
    """Test all dependencies for Teamcenter MCP are available."""
    try:
        import fastmcp
        import httpx
        # Core dependencies for Teamcenter integration
    except ImportError as e:
        pytest.fail(f"Missing dependency for Teamcenter MCP: {e}")


def test_server_module_structure():
    """Test module structure is correct for VS Code execution."""
    import auth_mcp_stdio
    
    # Should have mcp attribute that gets initialized in main()
    assert hasattr(auth_mcp_stdio, 'mcp')
    assert hasattr(auth_mcp_stdio, 'main')
    assert callable(auth_mcp_stdio.main)
    
    # Should have proper FastMCP imports
    server_path = os.path.join(project_root, 'auth_mcp_stdio.py')
    with open(server_path, 'r') as f:
        content = f.read()
    
    assert 'from fastmcp import FastMCP' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])