from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar


# Generic type for models
T = TypeVar("T")


class BaseRepository(ABC):
    """
    Persistence-agnostic repository contract.

    Defines the shape every Spartan repository must expose, independent of
    the underlying store (DynamoDB, SQL, in-memory, ...). Provider-specific
    implementations (e.g. DynamoDBRepository) implement these methods.
    """

    @abstractmethod
    def get_model_class(self) -> Type[T]:
        """Return the model class this repository handles."""

    @abstractmethod
    def get_entity_type(self) -> str:
        """Return the entity type this repository handles (e.g. 'PRODUCT')."""

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get an entity by ID."""

    @abstractmethod
    def save(self, entity: T) -> bool:
        """Save (create or update) an entity."""

    @abstractmethod
    def delete_by_id(self, entity_id: str) -> bool:
        """Hard delete an entity by ID."""

    @abstractmethod
    def soft_delete_by_id(self, entity_id: str) -> bool:
        """Soft delete an entity by ID, if the model supports it."""

    @abstractmethod
    def get_by_id_including_deleted(self, entity_id: str) -> Optional[T]:
        """Get an entity by ID, including soft-deleted ones."""

    @abstractmethod
    def list_by_entity_type(
        self,
        limit: int = 20,
        last_evaluated_key: Optional[dict] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        include_deleted: bool = False,
    ) -> Dict[str, Any]:
        """List entities of this repository's entity type, with pagination."""

    @abstractmethod
    def batch_get_by_ids(self, entity_ids: List[str]) -> List[T]:
        """Batch get entities by IDs."""

    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """Check whether an entity exists by ID."""
