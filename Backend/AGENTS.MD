# Agent Instructions for Kanyaraasi Backend

This document provides guidelines and conventions for AI agents (and human developers) working on this FastAPI backend project. Adhering to these will help maintain code quality, consistency, and ease of future development.

## 1. Project Structure Overview

*   **`app/`**: Main application code.
    *   **`main.py`**: FastAPI application entry point and creation.
    *   **`core/`**: Core components like database setup (`database.py`), settings (`settings.py`), and dependencies (`dependencies.py`).
    *   **`models/`**: SQLAlchemy ORM models.
        *   `common.py`: Defines `CommonModel` providing shared fields like `id`, `is_active`, `created_at`, `updated_at`. Most new models should inherit from this.
    *   **`schemas/`**: Pydantic schemas for data validation and serialization.
        *   Follow naming conventions: `ModelNameBase`, `ModelNameCreate`, `ModelNameUpdate`, `ModelNameResponse` (or `ModelNamePublic`).
    *   **`api/`**: API endpoint definitions.
        *   Endpoints are grouped by resource (e.g., `user/`, `document/`, `account/`).
        *   Each resource directory typically contains:
            *   An `endpoint_name.py` file for API routes (e.g., `user.py`, `auth.py`).
            *   A `function.py` file for business logic related to those endpoints.
    *   **`utils/`**: Utility functions and modules (e.g., `s3_utils.py`, `ocr.py`, `gemini.py`, `constant/globals.py`).
*   **`alembic/`**: Alembic database migration scripts and configuration.
    *   `env.py` is configured to detect model changes from `app.models` via `Base.metadata`. Ensure all new models are imported directly or indirectly in `env.py`.

## 2. Coding Conventions and Patterns

### Models (SQLAlchemy)

*   **Base Model**: Inherit from `app.models.common.CommonModel` for new tables to get `id` (Integer PK), `is_active`, `created_at`, `updated_at` fields automatically.
    *   If a model requires a different primary key type (e.g., String for `User.id`), it can override the `id` field from `CommonModel`.
*   **Relationships**: Define relationships with `back_populates` for bidirectionality. Use `cascade="all, delete-orphan"` for dependent objects where appropriate.
*   **Docstrings**: Add class and attribute docstrings explaining the model and its fields. Include `comment="description"` on `Column` for database schema comments.
*   **Enums**: Use enums from `app.utils.constant.globals.py` for fields like `role` or `status`. Use `SQLAlchemyEnum(PythonEnum)` in model definitions.

### Schemas (Pydantic)

*   **Naming**:
    *   `SchemaNameBase`: Common fields.
    *   `SchemaNameCreate`: For request bodies creating new resources.
    *   `SchemaNameUpdate`: For request bodies updating existing resources (often with all fields optional).
    *   `SchemaNameResponse` or `SchemaNamePublic`: For API responses.
*   **`orm_mode = True`**: (or `from_attributes = True` for Pydantic v2) should be set in the `Config` class for schemas that are populated from ORM model instances.
*   **Field Descriptions**: Use `Field(..., description="...", example="...")` for all schema fields to improve OpenAPI documentation.
*   **Specific Types**: Use Pydantic's specific types where applicable (e.g., `EmailStr`, `HttpUrl`, `Decimal`).
*   **Docstrings**: Add docstrings to all Pydantic models.

### API Endpoints (FastAPI)

*   **Structure**: Group related endpoints in APIRouters within resource-specific files (e.g., `app/api/endpoints/user/auth.py`).
*   **Business Logic**: Separate business logic into `function.py` files within the same module to keep endpoint files clean and focused on request/response handling.
*   **Schemas**: Use the defined Pydantic schemas for request body validation and response serialization (`response_model`).
*   **Dependencies**: Use FastAPI's `Depends` for injecting database sessions (`get_db`) and authenticated user objects (`get_current_user`).
*   **Error Handling**: Raise `HTTPException` with appropriate status codes and detail messages for API errors.
*   **Docstrings & OpenAPI**: Provide `summary`, `description`, and `tags` for routers and endpoints. Add detailed docstrings to endpoint functions.
*   **Background Tasks**: For long-running operations (e.g., OCR processing), use `BackgroundTasks` to avoid blocking the server.

### Utilities (`app/utils/`)

*   **Configuration**: Utilities requiring external service configurations (e.g., API keys, bucket names) should source these from `app.core.settings`.
*   **Error Handling**: Utility functions should generally raise specific custom exceptions or propagate underlying exceptions rather than just printing errors or returning `None` silently.
*   **Logging**: Use the `logging` module instead of `print()` statements.
*   **Asynchronous Operations**: If a utility function involves blocking I/O or is CPU-bound and is intended to be called from async code, ensure it's run in a thread pool (e.g., using `fastapi.concurrency.run_in_threadpool` or `asyncio.to_thread`).

### Database Migrations (Alembic)

*   **`env.py`**: Ensure this file imports all SQLAlchemy models so `autogenerate` can detect changes.
*   **Migration Scripts**: When generating new migrations (`alembic revision -m "description" --autogenerate`):
    *   Carefully review the generated script.
    *   Add comments explaining the purpose of the migration.
    *   For complex changes like column type changes on tables with data, or data transformations, you may need to write custom Python code within the migration script to handle data movement or updates.
*   **Schema Drift**: Be aware of the existing schema drift for the `User` table (ID type, name fields) as noted in the initial refactoring. Future migrations will need to address this carefully.

## 4. Configuration (`app.core.settings.py`)

*   All sensitive information (API keys, database credentials, secret keys) and environment-specific configurations (S3 bucket names, regions) MUST be loaded from environment variables via `pydantic-settings` (or similar) in `app.core.settings.py`.
*   Do not hardcode secrets in other parts of the codebase. Import them from `app.core.settings`.

## 5. General Quality

*   **Docstrings & Comments**: Write clear docstrings for all modules, classes, and functions. Add comments for complex or non-obvious code sections.
*   **Type Hinting**: Use type hints extensively.
*   **Error Handling**: Implement robust error handling.
*   **Logging**: Use the `logging` module for application logs.
*   **PEP 8**: Follow PEP 8 style guidelines.

By following these guidelines, we can ensure the backend remains maintainable, understandable, and robust.
