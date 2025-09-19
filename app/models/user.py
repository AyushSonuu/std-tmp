from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base_class import Base
from .rbac import user_role_association

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Add the many-to-many relationship to Role
    roles = relationship("Role", secondary=user_role_association, back_populates="users", lazy="selectin")