from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.permissions import AppPermissions
from app.crud import crud_rbac
from app.schemas.user import UserCreate
from app.schemas import rbac as rbac_schemas
from app.auth.auth import UserManager
from app.models.user import User
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserNotExists

SUPER_ADMIN_ROLE = "Super Admin"

async def seed_initial_data(db: AsyncSession):
    logger.info("Seeding initial data...")
    
    # 1. Create Super Admin role if it doesn't exist
    admin_role = await crud_rbac.crud_role.get_by_name(db, name=SUPER_ADMIN_ROLE)
    if not admin_role:
        admin_role_in = rbac_schemas.RoleCreate(
            name=SUPER_ADMIN_ROLE, 
            description="Full system access",
            permissions=[p.value for p in AppPermissions] # Grant all permissions
        )
        admin_role = await crud_rbac.crud_role.create(
            db, obj_in=admin_role_in
        )
    else:
        # Ensure the admin role always has all permissions
        admin_role.permissions = [p.value for p in AppPermissions]
        db.add(admin_role)
        await db.commit()
        await db.refresh(admin_role)


    # 2. Create the first superuser if it doesn't exist
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