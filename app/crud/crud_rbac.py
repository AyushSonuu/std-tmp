from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.rbac import Role, Permission
from app.models.user import User
from app.schemas.rbac import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Role | None:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Permission | None:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()
    
    async def get_or_create(self, db: AsyncSession, *, name: str, description: str) -> Permission:
        permission = await self.get_by_name(db, name=name)
        if not permission:
            permission_in = PermissionCreate(name=name, description=description)
            permission = await self.create(db, obj_in=permission_in)
        return permission


crud_role = CRUDRole(Role)
crud_permission = CRUDPermission(Permission)


async def assign_permission_to_role(db: AsyncSession, *, role: Role, permission: Permission) -> Role:
    if permission not in role.permissions:
        role.permissions.append(permission)
        await db.commit()
        await db.refresh(role)
    return role

async def remove_permission_from_role(db: AsyncSession, *, role: Role, permission: Permission) -> Role:
    if permission in role.permissions:
        role.permissions.remove(permission)
        await db.commit()
        await db.refresh(role)
    return role


async def assign_role_to_user(db: AsyncSession, *, user: User, role: Role) -> User:
    if role not in user.roles:
        user.roles.append(role)
        await db.commit()
        await db.refresh(user)
    return user

async def remove_role_from_user(db: AsyncSession, *, user: User, role: Role) -> User:
    if role in user.roles:
        user.roles.remove(role)
        await db.commit()
        await db.refresh(user)
    return user