from sqladmin import ModelView
from app.models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.password,
        User.role,
    ]
