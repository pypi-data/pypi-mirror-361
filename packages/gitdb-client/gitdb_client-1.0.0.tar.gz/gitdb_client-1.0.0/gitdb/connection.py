"""
Connection management for GitDB Python SDK
"""

import asyncio
import json
from typing import Any, Dict, Optional
import aiohttp
import requests
from .types import GitDBConfig, ConnectionStatus, GitDBConnectionError


class Connection:
    """Connection manager for GitDB"""
    
    def __init__(self, config: GitDBConfig):
        self.config = config
        self.connected = False
        self.base_url = f"http://{config.host}:{config.port}"
        self.timeout = config.timeout
        self.retries = config.retries
        
    async def connect(self) -> None:
        """Connect to GitDB server"""
        try:
            response = await self.make_request('/api/v1/collections/connect', {
                'method': 'POST',
                'json': {
                    'token': self.config.token,
                    'owner': self.config.owner,
                    'repo': self.config.repo
                }
            })
            
            if response.get('success'):
                self.connected = True
            else:
                raise GitDBConnectionError('Failed to connect to database', 500, response)
                
        except Exception as error:
            self.connected = False
            if isinstance(error, GitDBConnectionError):
                raise error
            raise GitDBConnectionError(
                f'Connection failed: {str(error)}',
                500,
                error
            )
    
    async def disconnect(self) -> None:
        """Disconnect from GitDB server"""
        try:
            await self.make_request('/api/v1/collections/disconnect', {
                'method': 'POST'
            })
        except Exception as error:
            # Don't throw on disconnect errors
            print(f'Disconnect warning: {error}')
        finally:
            self.connected = False
    
    async def get_status(self) -> ConnectionStatus:
        """Get connection status"""
        try:
            response = await self.make_request('/api/v1/collections/status', {
                'method': 'GET'
            })
            
            return ConnectionStatus(
                connected=response.get('connected', False),
                database=response.get('database'),
                error=None
            )
        except Exception as error:
            return ConnectionStatus(
                connected=False,
                database=None,
                error=str(error)
            )
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected
    
    async def ping(self) -> bool:
        """Ping the server"""
        try:
            response = await self.make_request('/health', {
                'method': 'GET'
            })
            return response == 'GraphQL Server is healthy'
        except Exception:
            return False
    
    async def health(self) -> Any:
        """Get health status"""
        return await self.make_request('/health', {
            'method': 'GET'
        })
    
    async def make_request(
        self,
        endpoint: str,
        options: Dict[str, Any],
        retry_count: int = 0
    ) -> Any:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            **options.get('headers', {})
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout / 1000)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                method = options.get('method', 'GET')
                json_data = options.get('json')
                data = options.get('data')
                
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    data=data
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise GitDBConnectionError(
                            f'HTTP {response.status}: {error_text}',
                            response.status,
                            {'url': url, 'status': response.status}
                        )
                    
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return await response.text()
                        
        except Exception as error:
            if isinstance(error, GitDBConnectionError):
                raise error
            
            # Retry logic for network errors
            if retry_count < self.retries and self._should_retry(error):
                delay = (2 ** retry_count) * 1  # Exponential backoff in seconds
                await asyncio.sleep(delay)
                return await self.make_request(endpoint, options, retry_count + 1)
            
            raise GitDBConnectionError(
                f'Request failed: {str(error)}',
                500,
                {'url': url, 'error': error}
            )
    
    def _should_retry(self, error: Exception) -> bool:
        """Check if request should be retried"""
        # Retry on network errors and timeouts
        if hasattr(error, 'code'):
            if error.code in ['ECONNREFUSED', 'ENOTFOUND', 'ETIMEDOUT']:
                return True
        return False
    
    def get_base_url(self) -> str:
        """Get base URL"""
        return self.base_url
    
    def get_config(self) -> GitDBConfig:
        """Get configuration"""
        return self.config 