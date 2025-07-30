"""
GitDB Python SDK
GitHub-backed NoSQL database client for Python
"""

from .client import GitDB, Collection
from .types import (
    GitDBConfig,
    Document,
    GitDBError,
    GitDBConnectionError,
    GitDBQueryError,
    GitDBValidationError,
)

__version__ = "1.0.0"
__author__ = "AFOT Team"
__email__ = "team@afot.com"

__all__ = [
    "GitDB",
    "Collection",
    "GitDBConfig",
    "Document",
    "GitDBError",
    "GitDBConnectionError",
    "GitDBQueryError",
    "GitDBValidationError",
] 