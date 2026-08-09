from abc import ABC, abstractmethod
from typing import Any, TypeVar


T = TypeVar("T")


class BaseService(ABC):
    """
    Persistence-agnostic service contract.

    Defines the shape every Spartan service should expose to its handlers,
    independent of the underlying repository or database. Concrete services
    implement these methods, typically by delegating to a repository that
    conforms to app.repositories.contracts.BaseRepository.
    """

    @abstractmethod
    def get_by_id(self, id: Any) -> T:
        """Retrieve a single entity by ID."""

    @abstractmethod
    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List entities, optionally paginated/filtered."""

    @abstractmethod
    def create(self, request: Any) -> T:
        """Create a new entity from a request model."""

    @abstractmethod
    def update(self, id: Any, request: Any) -> T:
        """Update an existing entity by ID from a request model."""

    @abstractmethod
    def delete(self, id: Any) -> Any:
        """Delete an entity by ID."""
