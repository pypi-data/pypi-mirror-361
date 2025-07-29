"""
Authenticated MCP server - STDIO transport with session-based authentication
This version handles the Azure AD + session cookie authentication flow
"""
from fastmcp import FastMCP
import httpx
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import re
import logging
import sys
import argparse
import os

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Send logs to stderr so they don't interfere with STDIO MCP protocol
    ]
)
logger = logging.getLogger(__name__)

# Global MCP server - will be initialized in main()
mcp = None

class AuthSession:
    """Manages authentication session for the MCP server"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.session_cookie: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        logger.info(f"🔧 AuthSession initialized with base_url: {self.base_url}")
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid (with 5-minute buffer)"""
        if not self.session_cookie or not self.expires_at:
            logger.debug("🔍 Session invalid: missing cookie or expiry")
            return False
        
        # Check expiry with 5-minute buffer (like the real client)
        buffer_time = timedelta(minutes=5)
        is_valid = datetime.now() < (self.expires_at - buffer_time)
        logger.debug(f"🔍 Session validity check: {is_valid}, expires at {self.expires_at}")
        return is_valid
    
    async def authenticate(self) -> bool:
        """Authenticate and get a new session cookie"""
        logger.info("🔐 Starting authentication process...")
        try:
            async with httpx.AsyncClient() as client:
                # Use a mock Bearer token (our API accepts any Bearer token)
                headers = {
                    "Authorization": "Bearer mcp_server_mock_token_12345",
                    "Content-Type": "application/json"
                }
                logger.debug(f"🔐 Calling {self.base_url}/api/login with headers: {headers}")
                
                response = await client.post(
                    f"{self.base_url}/api/login",
                    headers=headers
                )
                logger.debug(f"🔐 Login response: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                    return False
                
                # Extract session cookie from Set-Cookie header
                set_cookie = response.headers.get('set-cookie')
                logger.debug(f"🔐 Set-Cookie header: {set_cookie}")
                if not set_cookie:
                    logger.error("❌ No Set-Cookie header in login response")
                    return False
                
                # Parse codesess cookie
                cookie_match = re.search(r'codesess=([^;]+)', set_cookie)
                if not cookie_match:
                    logger.error("❌ No codesess cookie found")
                    return False
                
                self.session_cookie = cookie_match.group(1)
                logger.info(f"🔐 Extracted session cookie: {self.session_cookie[:8]}...")
                
                # Parse expiry from JSON response
                response_data = response.json()
                logger.debug(f"🔐 Login response data: {response_data}")
                expires_at_str = response_data.get('expires_at')
                if expires_at_str:
                    self.expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                else:
                    # Fallback: assume 55-minute expiry
                    self.expires_at = datetime.now() + timedelta(minutes=55)
                
                logger.info(f"✅ Authentication successful, session expires at {self.expires_at}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}", exc_info=True)
            return False
    
    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid session, authenticate if needed"""
        if self.is_session_valid():
            logger.debug("🔍 Session is valid, no authentication needed")
            return True
        
        logger.info("🔐 Session expired or missing, authenticating...")
        return await self.authenticate()
    
    def get_session_headers(self) -> dict:
        """Get headers with session cookie for authenticated requests"""
        if not self.session_cookie:
            return {}
        
        return {
            "Cookie": f"codesess={self.session_cookie}",
            "Content-Type": "application/json"
        }

# Global authentication session - will be initialized in main()
auth_session = None

async def teamcenter_search(search_query: str, topNDocuments: int = 5) -> str:
    """Search the Teamcenter knowledge base for technical information and documentation.
    
    This tool automatically handles authentication with the Teamcenter API.
    """
    logger.info(f"🔍 MCP Tool called: teamcenter_search('{search_query}', {topNDocuments})")
    
    # Ensure we have a valid session
    if not await auth_session.ensure_authenticated():
        logger.error("❌ Failed to authenticate with Teamcenter API")
        return "❌ Failed to authenticate with Teamcenter API"
    
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "search_query": search_query,
                "topNDocuments": topNDocuments
            }
            
            headers = auth_session.get_session_headers()
            
            response = await client.get(
                f"{auth_session.base_url}/stream",
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                print("🔐 Session expired during request, re-authenticating...")
                if await auth_session.authenticate():
                    # Retry with new session
                    headers = auth_session.get_session_headers()
                    response = await client.get(
                        f"{auth_session.base_url}/stream",
                        params=params,
                        headers=headers,
                        timeout=30.0
                    )
                else:
                    return "❌ Failed to re-authenticate with Teamcenter API"
            
            if response.status_code != 200:
                return f"❌ Teamcenter API error: {response.status_code} - {response.text}"
            
            # Parse SSE response and return accumulated content
            content = []
            citations = []
            
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data.get('type') == 'response':
                            content.append(data.get('data', ''))
                        elif data.get('type') == 'citation':
                            citations.append(data.get('data', ''))
                    except json.JSONDecodeError:
                        pass
            
            result = ''.join(content)
            if citations:
                result += "\n\nCitations:\n" + '\n'.join(citations)
            
            return result if result.strip() else "No results found for your query."
            
    except Exception as e:
        return f"❌ Error calling Teamcenter API: {str(e)}"

async def teamcenter_health_check() -> str:
    """Check if the Teamcenter KB API is healthy and authentication is working"""
    try:
        # Check basic API health
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{auth_session.base_url}/health", timeout=5.0)
            if response.status_code != 200:
                return f"❌ Teamcenter KB API health check failed: {response.status_code}"
        
        # Check authentication
        auth_status = await auth_session.ensure_authenticated()
        if not auth_status:
            return "❌ Teamcenter KB API is running but authentication failed"
        
        session_status = "valid" if auth_session.is_session_valid() else "expired"
        expires_info = f"expires at {auth_session.expires_at}" if auth_session.expires_at else "no expiry info"
        
        return f"✅ Teamcenter KB API is healthy\n🔐 Authentication: working\n📅 Session: {session_status} ({expires_info})"
        
    except Exception as e:
        return f"❌ Cannot reach Teamcenter KB API: {str(e)}"

async def teamcenter_session_info() -> str:
    """Get current authentication session information"""
    if not auth_session.session_cookie:
        return "❌ No active session"
    
    session_id_preview = auth_session.session_cookie[:8] + "..." if len(auth_session.session_cookie) > 8 else auth_session.session_cookie
    expires_info = str(auth_session.expires_at) if auth_session.expires_at else "unknown"
    is_valid = "✅ valid" if auth_session.is_session_valid() else "❌ expired"
    
    return f"🔐 Session ID: {session_id_preview}\n📅 Expires: {expires_info}\n✅ Status: {is_valid}"

def main():
    """Main entry point for the MCP server with command-line argument support"""
    parser = argparse.ArgumentParser(
        description="Teamcenter MCP Server - Authenticated Model Context Protocol server"
    )
    parser.add_argument(
        '--base-url', 
        type=str,
        help='Base URL of the Teamcenter API (defaults to TEAMCENTER_API_URL env var or http://localhost:8000)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='teamcenter-mcp-server 0.1.0'
    )
    
    # Add usage examples to help
    parser.epilog = """
Examples:
  # Use with local mock API (default)
  uv run python auth_mcp_stdio.py

  # Use with production Teamcenter API
  uv run python auth_mcp_stdio.py --base-url https://teamcenter.company.com

  # Use environment variable
  export TEAMCENTER_API_URL=https://teamcenter.company.com
  uv run python auth_mcp_stdio.py
    """
    
    args = parser.parse_args()
    
    # Initialize MCP server after argument parsing
    global mcp
    mcp = FastMCP(name="Teamcenter")
    
    # Re-register tools (since mcp was None when decorators ran)
    mcp.tool(teamcenter_search)
    mcp.tool(teamcenter_health_check)
    mcp.tool(teamcenter_session_info)
    
    # Determine base URL from args, env var, or default
    base_url = args.base_url or os.environ.get('TEAMCENTER_API_URL') or 'http://localhost:8000'
    
    # Initialize global auth session
    global auth_session
    auth_session = AuthSession(base_url)
    
    # Use STDIO transport - VS Code will manage this process
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()