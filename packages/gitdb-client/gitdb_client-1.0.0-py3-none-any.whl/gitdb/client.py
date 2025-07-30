"""
Main GitDB client for Python SDK
"""

import os
from typing import Any, Dict, List, Optional
from .connection import Connection
from .types import GitDBConfig, ConnectionStatus, Document


class GitDB:
    """Main GitDB client"""
    
    def __init__(self, config: GitDBConfig):
        self.config = config
        self.connection = Connection(config)
    
    async def connect(self) -> None:
        """Connect to GitDB"""
        await self.connection.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from GitDB"""
        await self.connection.disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connection.is_connected()
    
    async def get_status(self) -> ConnectionStatus:
        """Get connection status"""
        return await self.connection.get_status()
    
    async def ping(self) -> bool:
        """Ping the server"""
        return await self.connection.ping()
    
    async def health(self) -> Any:
        """Get health status"""
        return await self.connection.health()
    
    async def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            response = await self.connection.make_request('/api/v1/collections', {
                'method': 'GET'
            })
            
            if response.get('success'):
                return response.get('collections', [])
            else:
                raise Exception('Failed to list collections')
        except Exception as error:
            raise Exception(f'Failed to list collections: {str(error)}')
    
    async def create_collection(self, name: str) -> None:
        """Create a collection"""
        if not name or not isinstance(name, str):
            raise ValueError('Collection name must be a non-empty string')
        
        try:
            response = await self.connection.make_request('/api/v1/collections', {
                'method': 'POST',
                'json': {'name': name}
            })
            
            if not response.get('success'):
                raise Exception('Failed to create collection')
        except Exception as error:
            raise Exception(f'Failed to create collection: {str(error)}')
    
    async def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        if not name or not isinstance(name, str):
            raise ValueError('Collection name must be a non-empty string')
        
        try:
            response = await self.connection.make_request(f'/api/v1/collections/{name}', {
                'method': 'DELETE'
            })
            
            if not response.get('success'):
                raise Exception('Failed to delete collection')
        except Exception as error:
            raise Exception(f'Failed to delete collection: {str(error)}')
    
    def collection(self, name: str) -> 'Collection':
        """Get a collection reference"""
        if not self.is_connected():
            raise Exception('Not connected to database. Call connect() first.')
        return Collection(name, self.connection)
    
    async def use_collection(self, name: str) -> 'Collection':
        """Use a collection, creating it if it doesn't exist"""
        collections = await self.list_collections()
        if name not in collections:
            await self.create_collection(name)
        return self.collection(name)
    
    @classmethod
    def from_environment(cls) -> 'GitDB':
        """Create client from environment variables"""
        token = os.getenv('GITDB_TOKEN')
        owner = os.getenv('GITDB_OWNER')
        repo = os.getenv('GITDB_REPO')
        host = os.getenv('GITDB_HOST', 'localhost')
        port = int(os.getenv('GITDB_PORT', '7896'))
        
        if not token or not owner or not repo:
            raise ValueError(
                'Missing required environment variables: GITDB_TOKEN, GITDB_OWNER, GITDB_REPO'
            )
        
        config = GitDBConfig(
            token=token,
            owner=owner,
            repo=repo,
            host=host,
            port=port
        )
        
        return cls(config)
    
    @classmethod
    def from_config(cls, config: GitDBConfig) -> 'GitDB':
        """Create client from config"""
        return cls(config)


class Collection:
    """Collection for CRUD operations"""
    
    def __init__(self, name: str, connection: Connection):
        self.name = name
        self.connection = connection
    
    async def insert(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a document"""
        self._validate_document(document)
        
        try:
            response = await self.connection.make_request(
                f'/api/v1/collections/{self.name}/documents',
                {
                    'method': 'POST',
                    'json': document
                }
            )
            
            return {
                'success': response.get('success', False),
                'document': response.get('document'),
                'message': response.get('message')
            }
        except Exception as error:
            raise Exception(f'Failed to insert document: {str(error)}')
    
    async def find(self, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Find documents"""
        try:
            if query and query:
                # Use POST /find endpoint for queries
                response = await self.connection.make_request(
                    f'/api/v1/collections/{self.name}/documents/find',
                    {
                        'method': 'POST',
                        'json': query
                    }
                )
            else:
                # Use GET endpoint for all documents
                response = await self.connection.make_request(
                    f'/api/v1/collections/{self.name}/documents',
                    {'method': 'GET'}
                )
            
            return {
                'success': response.get('success', False),
                'documents': response.get('documents', []),
                'count': response.get('count', 0),
                'collection': self.name
            }
        except Exception as error:
            raise Exception(f'Failed to find documents: {str(error)}')
    
    async def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Find one document"""
        try:
            result = await self.find(query)
            documents = result.get('documents', [])
            return documents[0] if documents else None
        except Exception as error:
            raise Exception(f'Failed to find one document: {str(error)}')
    
    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        if not doc_id:
            raise ValueError('Document ID is required')
        
        try:
            response = await self.connection.make_request(
                f'/api/v1/collections/{self.name}/documents/{doc_id}',
                {'method': 'GET'}
            )
            
            return response.get('document') if response.get('success') else None
        except Exception as error:
            if '404' in str(error):
                return None
            raise Exception(f'Failed to find document by ID: {str(error)}')
    
    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents"""
        try:
            result = await self.find(query)
            return result.get('count', 0)
        except Exception as error:
            raise Exception(f'Failed to count documents: {str(error)}')
    
    async def update(self, doc_id: str, update: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document"""
        if not doc_id:
            raise ValueError('Document ID is required')
        self._validate_document(update)
        
        try:
            response = await self.connection.make_request(
                f'/api/v1/collections/{self.name}/documents/{doc_id}',
                {
                    'method': 'PUT',
                    'json': update
                }
            )
            
            return {
                'success': response.get('success', False),
                'document': response.get('document'),
                'modified_count': 1 if response.get('document') else 0,
                'message': response.get('message')
            }
        except Exception as error:
            raise Exception(f'Failed to update document: {str(error)}')
    
    async def delete(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        if not doc_id:
            raise ValueError('Document ID is required')
        
        try:
            response = await self.connection.make_request(
                f'/api/v1/collections/{self.name}/documents/{doc_id}',
                {'method': 'DELETE'}
            )
            
            return {
                'success': response.get('success', False),
                'deleted_count': 1 if response.get('success') else 0,
                'message': response.get('message')
            }
        except Exception as error:
            raise Exception(f'Failed to delete document: {str(error)}')
    
    def _validate_document(self, document: Any) -> None:
        """Validate document"""
        if not document or not isinstance(document, dict):
            raise ValueError('Document must be a valid object')
        
        if isinstance(document, list):
            raise ValueError('Document cannot be an array') 