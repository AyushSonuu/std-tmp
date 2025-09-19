from enum import Enum

class AppPermissions(str, Enum):
    """
    An enumeration of all permissions available in the application.
    Using a StrEnum makes it easy to use these permissions directly in API
    dependencies and database models.
    """

    # --- RBAC Management ---
    RBAC_MANAGE = "rbac:manage"
    """Allows managing roles and their permissions."""

    # --- User Management ---
    USERS_READ = "users:read"
    """Allows reading all user data."""
    USERS_MANAGE = "users:manage"
    """Allows creating, editing, and deleting users."""

    # --- Admin/Reporting ---
    REPORTS_VIEW = "reports:view"
    """Allows viewing admin reports."""

    # --- Payments ---
    PAYMENTS_CREATE = "payments:create"
    """Allows creating payments."""

# You can add more permission constants here as your application grows.

# --- Permission Actions ---
# These can be useful for dynamic permission generation if needed
ACTION_READ = "read"
ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete" 