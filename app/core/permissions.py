# --- Permission Actions ---
ACTION_READ = "read"
ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"

"""
This file centralizes all permission strings used in the application.
Using constants for permission names helps avoid typos and makes the code
more maintainable. It also provides a single source of truth for all
available permissions.
"""

# --- RBAC Management Permissions ---
RBAC_MANAGE = "rbac:manage"
RBAC_MANAGE_DESCRIPTION = "Allows managing roles and permissions."

# --- User Management Permissions ---
USERS_READ = "users:read"
USERS_READ_DESCRIPTION = "Allows reading all user data."

USERS_MANAGE = "users:manage"
USERS_MANAGE_DESCRIPTION = "Allows creating, editing, and deleting users."

# --- Admin/Reporting Permissions ---
REPORTS_VIEW = "reports:view"
REPORTS_VIEW_DESCRIPTION = "Allows viewing admin reports."

# --- E-commerce / Billing Permissions ---
PAYMENTS_CREATE = "payments:create"
PAYMENTS_CREATE_DESCRIPTION = "Allows creating payments."

# You can add more permission constants here as your application grows.
# For example:
# PRODUCTS_MANAGE = "products:manage"
# PRODUCTS_MANAGE_DESCRIPTION = "Allows managing product inventory." 