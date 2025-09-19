from sqlalchemy import Column, Integer, String, Table, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base_class import Base

# Association table for User <-> Role (many-to-many)
user_role_association = Table(
    "user_role_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    
    permissions: Mapped[list[str]] = mapped_column(JSON, default=[], server_default="[]")
    
    users = relationship("User", secondary=user_role_association, back_populates="roles", lazy="selectin")