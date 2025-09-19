from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core import permissions as perms
from app.crud import crud_rbac
from app.schemas.user import UserCreate
from app.schemas import rbac as rbac_schemas
from app.auth.auth import UserManager
from app.models.user import User
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserNotExists

# The single permission required to bootstrap the RBAC system.
# All other permissions and roles are to be created dynamically via the API.
CORE_PERMISSION = {"name": perms.RBAC_MANAGE, "description": perms.RBAC_MANAGE_DESCRIPTION}

SUPER_ADMIN_ROLE = "Super Admin"

async def seed_initial_data(db: AsyncSession):
    logger.info("Seeding initial data...")
    
    # 1. Create the core permission for RBAC management
    rbac_manage_perm = await crud_rbac.crud_permission.get_or_create(
        db, name=CORE_PERMISSION["name"], description=CORE_PERMISSION["description"]
    )

    # 2. Create Super Admin role
    admin_role = await crud_rbac.crud_role.get_by_name(db, name=SUPER_ADMIN_ROLE)
    if not admin_role:
        admin_role = await crud_rbac.crud_role.create(
            db, obj_in=rbac_schemas.RoleCreate(name=SUPER_ADMIN_ROLE, description="Full system access")
        )

    # 3. Assign the core permission to the Super Admin role
    if rbac_manage_perm not in admin_role.permissions:
        await crud_rbac.assign_permission_to_role(db, role=admin_role, permission=rbac_manage_perm)

    # 4. Create the first superuser if it doesn't exist
    user_db = SQLAlchemyUserDatabase(db, User)
    user_manager = UserManager(user_db)
    try:
        await user_manager.get_by_email(settings.FIRST_SUPERUSER_EMAIL)
    except UserNotExists:
        new_user = await user_manager.create(
            UserCreate(email=settings.FIRST_SUPERUSER_EMAIL, password=settings.FIRST_SUPERUSER_PASSWORD),
            safe=True
        )
        await crud_rbac.assign_role_to_user(db, user=new_user, role=admin_role)
        logger.info(f"Created first superuser: {settings.FIRST_SUPERUSER_EMAIL}")

    logger.info("Initial data seeding complete.")