"""
Authentication models for type safety and convention compliance.

This module defines the User type that is returned by get_current_user dependency
and used throughout the application for authentication and authorization.
"""

from typing import List, Literal, Optional, TypedDict


class User(TypedDict, total=False):
    """
    User type returned by get_current_user dependency.

    This type follows the convention expected by all endpoints that use
    `user: User = Depends(get_current_user)` dependency injection.

    Fields:
        username: Unique identifier for the user
        user_type: Role type (admin, member, readonly, guest, suspended)
        permissions: List of permission strings
        cognito:groups: Cognito groups for AWS integration
        auth_method: How the user was authenticated (jwt, api_key, test)
        test_user_type: Optional field for test users
        user_id: Optional user ID for additional identification
    """

    username: str
    user_type: Literal[
        "superadmin",
        "admin",
        "member",
        "readonly",
        "guest",
        "suspended",
        "service",
    ]
    permissions: List[str]
    auth_method: Literal["jwt", "api_key", "test"]
    # Optional fields
    user_id: Optional[str]
    test_user_type: Optional[str]
    email: Optional[str]


# Type alias for backward compatibility
AuthUser = User


# Convenience type for service authentication
class ServiceUser(User):
    """Service account user type for API key authentication."""

    username: str = "service-account"
    user_type: Literal["service"] = "service"
    auth_method: Literal["api_key"] = "api_key"
    permissions: List[str] = ["read", "write", "delete", "admin"]


# Permission constants following convention
PERMISSIONS = {
    "READ": "read",
    "WRITE": "write",
    "DELETE": "delete",
    "ADMIN": "admin",
}

# Role-to-permissions mapping following convention
ROLE_PERMISSIONS = {
    "superadmin": ["read", "write", "delete", "admin"],  # Highest privilege
    "admin": ["read", "write", "delete", "admin"],
    "member": ["read", "write"],
    "readonly": ["read"],
    "guest": ["read"],  # Limited read access
    "suspended": [],  # No permissions
    "service": ["read", "write", "delete", "admin"],
}


def get_permissions_for_role(role: str) -> List[str]:
    """Get permissions list for a given role following convention."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission."""
    return permission in user.get("permissions", [])


def has_any_permission(user: User, permissions: List[str]) -> bool:
    """Check if user has any of the specified permissions."""
    user_permissions = user.get("permissions", [])
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(user: User, permissions: List[str]) -> bool:
    """Check if user has all of the specified permissions."""
    user_permissions = user.get("permissions", [])
    return all(perm in user_permissions for perm in permissions)


def is_suspended(user: User) -> bool:
    """Check if user is suspended (always returns 403)."""
    return user.get("user_type") == "suspended"
