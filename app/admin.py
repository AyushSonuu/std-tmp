from sqladmin import Admin, ModelView
from .models import user, rbac

class UserAdmin(ModelView, model=user.User):
    column_list = [user.User.id, user.User.email, user.User.is_active, user.User.roles]
    column_details_exclude_list = [user.User.hashed_password]
    can_create = False  # Users should be created via the registration endpoint
    form_columns = [user.User.email, user.User.is_active, user.User.is_superuser, user.User.roles]

class RoleAdmin(ModelView, model=rbac.Role):
    column_list = [rbac.Role.id, rbac.Role.name, rbac.Role.description, rbac.Role.permissions]
    form_include_pk = True

class PermissionAdmin(ModelView, model=rbac.Permission):
    column_list = [rbac.Permission.id, rbac.Permission.name, rbac.Permission.description]
    form_include_pk = True

def setup_admin(app, engine):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(PermissionAdmin) 