# Import all the models, so that Alembic can see them
from app.models.base_class import Base
from app.models.user import User
from app.models.rbac import Role, Permission