# Repository package for data access layer

from .contracts import BaseRepository
from .dynamodb import DynamoDBRepository


__all__ = [
    "BaseRepository",
    "DynamoDBRepository",
]
