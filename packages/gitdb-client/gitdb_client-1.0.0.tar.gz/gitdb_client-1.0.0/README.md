# GitDB Python SDK

Official Python client for GitDB - GitHub-backed NoSQL database.

## Features

- 🚀 **Easy to use** - Familiar MongoDB-like API
- 🔗 **Connection management** - Automatic reconnection and health checks
- 📊 **GraphQL support** - Full GraphQL client with introspection
- 🔒 **Type safety** - Full type hints and Pydantic models
- ⚡ **Async support** - Modern async/await API
- 🛡️ **Error handling** - Comprehensive error types and handling
- 🔧 **Flexible configuration** - Environment variables and custom config

## Installation

```bash
pip install gitdb-client
```

## Quick Start

### Basic Usage

```python
import asyncio
from gitdb import GitDB

async def main():
    # Initialize client
    db = GitDB.from_environment()
    
    # Connect and use
    await db.connect()
    
    users = db.collection('users')
    
    # Insert a document
    user = await users.insert({
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    })
    
    # Find documents
    all_users = await users.find()
    john = await users.find_one({'name': 'John Doe'})
    
    # Update document
    await users.update(user['document']['_id'], {'age': 31})
    
    # Delete document
    await users.delete(user['document']['_id'])
    
    await db.disconnect()

# Run the example
asyncio.run(main())
```

### Environment Variables

```python
import os

# Set environment variables
os.environ['GITDB_TOKEN'] = 'ghp_your_github_token_here'
os.environ['GITDB_OWNER'] = 'your-username'
os.environ['GITDB_REPO'] = 'your-database-repo'
os.environ['GITDB_HOST'] = 'localhost'
os.environ['GITDB_PORT'] = '7896'

# Use from environment
db = GitDB.from_environment()
```

## API Reference

### GitDB Client

#### Constructor

```python
GitDB(config: GitDBConfig)
```

**Config Options:**
- `token` (required): GitHub personal access token
- `owner` (required): GitHub username or organization
- `repo` (required): GitHub repository name
- `host` (optional): GitDB server host (default: 'localhost')
- `port` (optional): GitDB server port (default: 7896)
- `timeout` (optional): Request timeout in ms (default: 30000)
- `retries` (optional): Number of retry attempts (default: 3)

#### Methods

```python
# Connection management
await db.connect(): None
await db.disconnect(): None
db.is_connected(): bool
await db.get_status(): ConnectionStatus
await db.ping(): bool
await db.health(): Any

# Collection management
db.collection(name: str): Collection
await db.list_collections(): List[str]
await db.create_collection(name: str): None
await db.delete_collection(name: str): None

# Utility methods
await db.use_collection(name: str): Collection

# Static methods
GitDB.from_environment(): GitDB
GitDB.from_config(config: GitDBConfig): GitDB
```

### Collection API

#### Methods

```python
# Create operations
await collection.insert(document: Dict[str, Any]): Dict[str, Any]

# Read operations
await collection.find(query: Optional[Dict[str, Any]] = None): Dict[str, Any]
await collection.find_one(query: Optional[Dict[str, Any]] = None): Optional[Dict[str, Any]]
await collection.find_by_id(id: str): Optional[Dict[str, Any]]
await collection.count(query: Optional[Dict[str, Any]] = None): int

# Update operations
await collection.update(id: str, update: Dict[str, Any]): Dict[str, Any]

# Delete operations
await collection.delete(id: str): Dict[str, Any]
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_test.py` - Basic connection and operations
- `crud_test.py` - CRUD operations
- `graphql_test.py` - GraphQL queries and mutations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 