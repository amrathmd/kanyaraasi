# admin.py
# Defines admin views for SQLAlchemy models using the `sqladmin` library.
# These views configure how models are displayed and managed in the admin interface.

from sqladmin import ModelView
from app.models.user import User # Import the User model to be administered

# It's good practice to also import other models that will have admin views.
# from app.models.account import Account
# from app.models.document import Document
# from app.models.document_info import DocumentInfo

class UserAdmin(ModelView, model=User):
    """
    Admin view configuration for the User model.

    This class defines how the User model is presented and managed within the
    SQLAdmin interface.
    """
    # Display name for the User model in the admin navigation
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user" # Example: FontAwesome icon

    # Columns to display in the list view of users.
    # Consider security implications: User.password (hashed) is included.
    # It's generally not recommended to display password hashes directly in list views.
    # Common practice might be to omit it or show a placeholder if editing is done via a form.
    column_list = [
        User.id,
        User.name, # Added name for better identification
        User.email,
        User.role,
        User.is_active, # Added is_active from CommonModel
        User.created_at # Added created_at from CommonModel
        # User.password, # Consider removing User.password from list view for security
    ]

    # Columns that can be searched in the admin list view.
    column_searchable_list = [
        User.name,
        User.email,
    ]

    # Columns that can be sorted in the admin list view.
    column_sortable_list = [
        User.id,
        User.name,
        User.email,
        User.role,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]

    # Columns to include in the create/edit forms.
    # `CommonModel` fields like `id`, `created_at`, `updated_at` are usually excluded from forms
    # as they are auto-managed. `is_active` might be included.
    form_columns = [
        User.name,
        User.email,
        # User.password, # For password, consider a custom form field for hashing new passwords
        User.role,
        User.is_active,
    ]

    # If you need to handle password hashing when a user is created/updated via admin:
    # You might need to override `on_model_change` and `on_model_create` methods
    # to hash the password before saving.
    # Example (conceptual, requires password hashing utility):
    #
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    #
    # async def on_model_change(self, data: dict, model: Any, is_created: bool, session: AsyncSession) -> None:
    #     if 'password' in data and data['password']:
    #         # This is a simplified example. In a real scenario, you'd check if the password was actually changed.
    #         # For existing models, you might only hash if data['password'] is not already a hash or is explicitly being set.
    #         data['password'] = pwd_context.hash(data['password'])
    #     await super().on_model_change(data, model, is_created, session)


# Example for other models (these would typically be in their own Admin classes):
# class AccountAdmin(ModelView, model=Account):
#     name = "Account"
#     name_plural = "Accounts"
#     icon = "fa-solid fa-piggy-bank"
#     column_list = [Account.id, Account.user_id, Account.year, Account.available_balance, Account.is_active]
#     form_columns = [Account.user, Account.year, Account.total_balance, Account.available_balance, Account.is_active]

# class DocumentAdmin(ModelView, model=Document):
#     name = "Document"
#     name_plural = "Documents"
#     icon = "fa-solid fa-file-alt"
#     column_list = [Document.id, Document.document_id, Document.user_id, Document.status, Document.is_active, Document.created_at]
#     # ... other configurations
