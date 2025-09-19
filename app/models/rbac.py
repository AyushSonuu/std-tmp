from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base_class import Base # Assuming you have a Base class for your models

# Association table for User <-> Role (many-to-many)
user_role_association = Table(
    "user_role_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Role <-> Permission (many-to-many)
role_permission_association = Table(
    "role_permission_association",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles", lazy="selectin")
    users = relationship("User", secondary=user_role_association, back_populates="roles", lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions", lazy="selectin")