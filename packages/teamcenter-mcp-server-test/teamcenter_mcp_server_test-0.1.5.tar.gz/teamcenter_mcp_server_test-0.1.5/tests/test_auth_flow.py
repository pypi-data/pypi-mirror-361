"""
Test the complete authentication flow to verify mock API mimics real Teamcenter API
"""
import httpx
import pytest
import json


@pytest.mark.asyncio
async def test_full_authentication_flow():
    """Test the complete auth flow: login -> get session -> use session for API calls."""
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8000"
        
        # Step 1: Login with Bearer token to get session cookie
        login_headers = {
            "Authorization": "Bearer mock_azure_ad_token_12345",
            "X-Refresh-Token": "mock_refresh_token"
        }
        
        login_response = await client.post(
            f"{base_url}/api/login",
            headers=login_headers
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["message"] == "Authentication successful"
        assert "session_id" in login_data
        assert "expires_at" in login_data
        
        # Extract session cookie from Set-Cookie header
        set_cookie = login_response.headers.get("set-cookie")
        assert set_cookie is not None
        assert "codesess=" in set_cookie
        
        # Parse the session ID from the cookie
        session_id = None
        for part in set_cookie.split(";"):
            if part.strip().startswith("codesess="):
                session_id = part.strip().split("=", 1)[1]
                break
        
        assert session_id is not None
        print(f"Got session ID: {session_id}")
        
        # Step 2: Use session cookie for authenticated API calls
        session_headers = {
            "Cookie": f"codesess={session_id}"
        }
        
        # Test /stream endpoint with authentication
        stream_response = await client.get(
            f"{base_url}/stream",
            params={
                "search_query": "authentication test query",
                "topNDocuments": 2
            },
            headers=session_headers
        )
        
        assert stream_response.status_code == 200
        assert stream_response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Verify streaming content
        content = stream_response.text
        assert "data: " in content
        assert '"type": "metadata"' in content
        assert '"type": "response"' in content
        assert '"type": "citation"' in content
        
        # Test /add_rating endpoint with authentication  
        rating_payload = {
            "chat_id": "test_auth_session_123",
            "search_query": "authentication test query",
            "rating": 4.5
        }
        
        rating_response = await client.post(
            f"{base_url}/add_rating",
            json=rating_payload,
            headers=session_headers
        )
        
        assert rating_response.status_code == 200
        rating_data = rating_response.json()
        assert rating_data["message"] == "Rating added successfully"


@pytest.mark.asyncio 
async def test_unauthenticated_access_denied():
    """Test that protected endpoints reject requests without valid session."""
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8000"
        
        # Try to access /stream without authentication
        stream_response = await client.get(
            f"{base_url}/stream",
            params={
                "search_query": "unauthorized test",
                "topNDocuments": 2
            }
        )
        
        assert stream_response.status_code == 401
        error_data = stream_response.json()
        assert "Authentication required" in error_data["detail"]
        
        # Try to access /add_rating without authentication
        rating_payload = {
            "chat_id": "unauthorized_session",
            "search_query": "unauthorized test",
            "rating": 3.0
        }
        
        rating_response = await client.post(
            f"{base_url}/add_rating",
            json=rating_payload
        )
        
        assert rating_response.status_code == 401
        error_data = rating_response.json()
        assert "Authentication required" in error_data["detail"]


@pytest.mark.asyncio
async def test_invalid_session_cookie():
    """Test that invalid session cookies are rejected."""
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8000"
        
        # Try with invalid session cookie
        invalid_headers = {
            "Cookie": "codesess=invalid_session_id_12345"
        }
        
        stream_response = await client.get(
            f"{base_url}/stream",
            params={
                "search_query": "invalid session test",
                "topNDocuments": 2
            },
            headers=invalid_headers
        )
        
        assert stream_response.status_code == 401
        error_data = stream_response.json()
        assert "Session expired or invalid" in error_data["detail"]


@pytest.mark.asyncio
async def test_login_with_invalid_bearer_token():
    """Test that login fails with invalid Bearer token format."""
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8000"
        
        # Try login with invalid authorization header
        invalid_headers = {
            "Authorization": "InvalidFormat some_token_123"
        }
        
        login_response = await client.post(
            f"{base_url}/api/login",
            headers=invalid_headers
        )
        
        assert login_response.status_code == 401
        error_data = login_response.json()
        assert "Invalid authorization format" in error_data["detail"]


@pytest.mark.asyncio
async def test_session_cookie_format():
    """Test that the session cookie has the correct format and attributes."""
    async with httpx.AsyncClient() as client:
        base_url = "http://127.0.0.1:8000"
        
        login_headers = {
            "Authorization": "Bearer test_token_for_cookie_format",
        }
        
        login_response = await client.post(
            f"{base_url}/api/login",
            headers=login_headers
        )
        
        assert login_response.status_code == 200
        
        # Check Set-Cookie header format
        set_cookie = login_response.headers.get("set-cookie")
        assert set_cookie is not None
        
        # Verify cookie attributes
        assert "codesess=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "Path=/" in set_cookie
        assert "Max-Age=3300" in set_cookie  # 55 minutes in seconds
        assert "SameSite=Lax" in set_cookie


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_full_authentication_flow())