from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.rbac import Role
from app.models.user import User
from app.schemas.rbac import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Role | None:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()


crud_role = CRUDRole(Role)


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