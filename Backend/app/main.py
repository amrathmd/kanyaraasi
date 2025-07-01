# main.py
# Main application file for the FastAPI backend.
# This file initializes the FastAPI application, sets up database tables,
# configures middleware, and includes API routers.

from fastapi import FastAPI

# Database engine for creating tables
from app.core.database import engine

# Helper functions for router initialization and middleware configuration
from app.core.modules import init_routers, make_middleware

# Import all SQLAlchemy models to ensure their tables are created.
# These imports are necessary for Base.metadata.create_all(bind=engine) to work correctly.
import app.models.user
import app.models.account
import app.models.document
import app.models.document_info
# Note: app.models.admin is not imported here, if it contains Base metadata, it should be imported.


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    This function performs the following key operations:
    1. Creates all database tables defined by the SQLAlchemy models.
       It appears there's a duplicate line for `app.models.document_info.Base.metadata.create_all(bind=engine)`.
       This will be corrected.
    2. Initializes the FastAPI application with title, description, version, and middleware.
    3. Initializes all API routers.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Create database tables for all imported models
    # It's good practice to have a single Base for all models or ensure all relevant Bases are called.
    # Consolidating these calls or ensuring all models are covered by a central Base is recommended.
    app.models.user.Base.metadata.create_all(bind=engine)
    app.models.account.Base.metadata.create_all(bind=engine)
    app.models.document.Base.metadata.create_all(bind=engine)
    app.models.document_info.Base.metadata.create_all(bind=engine)
    # Removed duplicate: app.models.document_info.Base.metadata.create_all(bind=engine)

    # Initialize the FastAPI application
    app_ = FastAPI(
        title="kanyaraasi",
        description="Backend project to automate wellness claims",
        version="1.0.0",
        # Example for dependencies: dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )

    # Include all API routers from app.api.routers
    init_routers(app_=app_)

    return app_


# Create the FastAPI application instance
# This instance will be used by Uvicorn or a similar ASGI server to run the application.
app = create_app()
