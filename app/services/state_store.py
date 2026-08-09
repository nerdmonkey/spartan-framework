from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseStateStore(ABC):
    """
    Persistence-agnostic key/value state store contract.

    Defines the shape every Spartan state store must expose, independent of
    the underlying store (DynamoDB, SQL, in-memory, ...). Provider-specific
    implementations (e.g. AppService for DynamoDB) implement these methods.
    """

    @abstractmethod
    def set_state(self, key: str, value: Any) -> Any:
        """Set or update the state value for the given key."""

    @abstractmethod
    def get_state(self, key: str) -> Optional[Any]:
        """Get the state value for the given key, or None if not found."""

    @abstractmethod
    def remove_state(self, key: str) -> Any:
        """Remove the state value for the given key."""
