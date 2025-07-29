"""
QUADS authentication management.
Handles automatic login and token management for QUADS API calls.
"""

import asyncio
import time
from typing import Optional, Dict, Any
import httpx


class QuadsAuthManager:
    """
    Manages authentication for QUADS API calls.
    Automatically handles login and token refresh.
    """
    
    def __init__(self, base_url: str, username: Optional[str] = None, 
                 password: Optional[str] = None, auth_token: Optional[str] = None,
                 timeout: int = 30, verify_ssl: bool = True):
        """
        Initialize the authentication manager.
        
        Args:
            base_url: QUADS API base URL
            username: Username for authentication (if using username/password)
            password: Password for authentication (if using username/password)
            auth_token: Pre-existing auth token (if available)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates (set False for self-signed)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Token management
        self._auth_token: Optional[str] = auth_token
        self._token_expires_at: Optional[float] = None
        self._login_lock = asyncio.Lock()
        
        # Assume tokens are valid for 1 hour if no expiry info
        self._token_ttl = 3600  # 1 hour in seconds
    
    @property
    def has_credentials(self) -> bool:
        """Check if we have either username/password or a token."""
        return (self.username and self.password) or self._auth_token is not None
    
    @property
    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self._auth_token:
            return False
        
        if self._token_expires_at is None:
            # No expiry info, assume it's still valid for a reasonable time
            return True
        
        # Check if token expires in the next 60 seconds (refresh early)
        return time.time() < (self._token_expires_at - 60)
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        Automatically handles login if needed.
        
        Returns:
            Dictionary with authentication headers
        """
        if not self.has_credentials:
            return {}
        
        # If we don't have a valid token, try to get one
        if not self.is_token_valid:
            await self._ensure_authenticated()
        
        if self._auth_token:
            return {"Authorization": f"Bearer {self._auth_token}"}
        
        return {}
    
    async def _ensure_authenticated(self) -> None:
        """
        Ensure we have a valid authentication token.
        Performs login if necessary.
        """
        async with self._login_lock:
            # Check again after acquiring lock
            if self.is_token_valid:
                return
            
            if not (self.username and self.password):
                # No credentials to perform login
                return
            
            try:
                await self._perform_login()
            except Exception as e:
                # Log the error but don't raise - let the API call fail gracefully
                print(f"Warning: Failed to authenticate with QUADS: {e}")
    
    async def _perform_login(self) -> None:
        """
        Perform login to QUADS API and store the token.
        """
        login_url = f"{self.base_url}/login/"
        
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(
                login_url,
                auth=(self.username, self.password),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "auth_token" in result:
                self._auth_token = result["auth_token"]
                # Set expiry time (assume 1 hour if not specified)
                self._token_expires_at = time.time() + self._token_ttl
                print(f"✅ Successfully authenticated with QUADS API")
            else:
                raise ValueError("Login response did not contain auth_token")
    
    async def logout(self) -> None:
        """
        Logout from QUADS API and invalidate the token.
        """
        if not self._auth_token:
            return
        
        try:
            logout_url = f"{self.base_url}/logout/"
            headers = {"Authorization": f"Bearer {self._auth_token}"}
            
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                await client.post(logout_url, headers=headers, timeout=self.timeout)
            
            print("✅ Successfully logged out from QUADS API")
        except Exception as e:
            print(f"Warning: Failed to logout from QUADS: {e}")
        finally:
            # Clear token regardless of logout success
            self._auth_token = None
            self._token_expires_at = None
    
    async def make_authenticated_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make an authenticated HTTP request to QUADS API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL or path (if starts with /, will be appended to base_url)
            **kwargs: Additional arguments for httpx request
            
        Returns:
            HTTP response
        """
        # Handle relative URLs
        if url.startswith('/'):
            url = self.base_url + url
        elif not url.startswith('http'):
            url = f"{self.base_url}/{url}"
        
        # Get authentication headers
        auth_headers = await self.get_auth_headers()
        
        # Merge with any existing headers
        headers = kwargs.get('headers', {})
        headers.update(auth_headers)
        kwargs['headers'] = headers
        
        # Set timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.request(method, url, **kwargs)
            
            # If we get a 401, try to re-authenticate once
            if response.status_code == 401 and self.username and self.password:
                # Clear current token and try to login again
                self._auth_token = None
                self._token_expires_at = None
                
                # Get fresh auth headers
                auth_headers = await self.get_auth_headers()
                headers.update(auth_headers)
                kwargs['headers'] = headers
                
                # Retry the request
                response = await client.request(method, url, **kwargs)
            
            return response


# Global auth manager instance - will be initialized by server.py
auth_manager: Optional[QuadsAuthManager] = None


def get_auth_manager() -> Optional[QuadsAuthManager]:
    """Get the global authentication manager instance."""
    return auth_manager


def set_auth_manager(manager: QuadsAuthManager) -> None:
    """Set the global authentication manager instance."""
    global auth_manager
    auth_manager = manager