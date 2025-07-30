"""
Type definitions for GitDB Python SDK
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class GitDBConfig(BaseModel):
    """Configuration for GitDB client"""
    token: str = Field(..., description="GitHub personal access token")
    owner: str = Field(..., description="GitHub username or organization")
    repo: str = Field(..., description="GitHub repository name")
    host: str = Field(default="localhost", description="GitDB server host")
    port: int = Field(default=7896, description="GitDB server port")
    timeout: int = Field(default=30000, description="Request timeout in milliseconds")
    retries: int = Field(default=3, description="Number of retry attempts")
    pool_size: Optional[int] = Field(default=None, description="Connection pool size")


class ConnectionStatus(BaseModel):
    """Connection status information"""
    connected: bool = Field(..., description="Whether connected to database")
    database: Optional[Dict[str, str]] = Field(default=None, description="Database info")
    error: Optional[str] = Field(default=None, description="Connection error message")


class Document(BaseModel):
    """Document model"""
    id: str = Field(..., description="Document ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Document data")


class QueryOptions(BaseModel):
    """Query options for find operations"""
    limit: Optional[int] = Field(default=None, description="Maximum number of documents")
    skip: Optional[int] = Field(default=None, description="Number of documents to skip")
    sort: Optional[Dict[str, int]] = Field(default=None, description="Sort criteria")
    projection: Optional[Dict[str, int]] = Field(default=None, description="Field projection")


class UpdateOptions(BaseModel):
    """Options for update operations"""
    upsert: bool = Field(default=False, description="Create if doesn't exist")
    multi: bool = Field(default=False, description="Update multiple documents")


class InsertResult(BaseModel):
    """Result of insert operation"""
    success: bool = Field(..., description="Whether operation was successful")
    document: Document = Field(..., description="Inserted document")
    message: Optional[str] = Field(default=None, description="Result message")


class FindResult(BaseModel):
    """Result of find operation"""
    success: bool = Field(..., description="Whether operation was successful")
    documents: List[Document] = Field(default_factory=list, description="Found documents")
    count: int = Field(default=0, description="Number of documents found")
    collection: str = Field(..., description="Collection name")


class UpdateResult(BaseModel):
    """Result of update operation"""
    success: bool = Field(..., description="Whether operation was successful")
    document: Optional[Document] = Field(default=None, description="Updated document")
    modified_count: int = Field(default=0, description="Number of documents modified")
    message: Optional[str] = Field(default=None, description="Result message")


class DeleteResult(BaseModel):
    """Result of delete operation"""
    success: bool = Field(..., description="Whether operation was successful")
    deleted_count: int = Field(default=0, description="Number of documents deleted")
    message: Optional[str] = Field(default=None, description="Result message")


class GraphQLResult(BaseModel):
    """Result of GraphQL operation"""
    data: Optional[Dict[str, Any]] = Field(default=None, description="Query result data")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="GraphQL errors")


class GitDBError(Exception):
    """Base exception for GitDB errors"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class GitDBConnectionError(GitDBError):
    """Connection-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message, "CONNECTION_ERROR", details)
        self.status_code = status_code


class GitDBQueryError(GitDBError):
    """Query-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message, "QUERY_ERROR", details)
        self.status_code = status_code


class GitDBValidationError(GitDBError):
    """Validation errors"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


# MongoDB-style query operators
class QueryOperator(str, Enum):
    """MongoDB-style query operators"""
    EQ = "$eq"
    NE = "$ne"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    IN = "$in"
    NIN = "$nin"
    EXISTS = "$exists"
    REGEX = "$regex"
    OPTIONS = "$options"
    AND = "$and"
    OR = "$or"
    NOT = "$not"
    NOR = "$nor"


# Type aliases for better readability
MongoStyleQuery = Dict[str, Any]
QueryFilter = Dict[str, Any] 