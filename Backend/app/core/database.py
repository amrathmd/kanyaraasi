# database.py
# Configures the database connection and session management for the application
# using SQLAlchemy.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os # For potentially using environment variables for database URL

# --- Database URL Configuration ---
# The URL for connecting to the database.
# Currently configured for a local SQLite database named 'sqlite.db' in the project root.
# For production, it's highly recommended to use a more robust database like PostgreSQL or MySQL,
# and to load the database URL from environment variables.
# Example for PostgreSQL using environment variable:
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

# --- SQLAlchemy Engine Setup ---
# The engine is the starting point for any SQLAlchemy application.
# It's a global object that manages database connections.
# `connect_args={"check_same_thread": False}` is specific to SQLite and allows
# the connection to be shared across threads. This is necessary for FastAPI's
# default behavior of handling requests in separate threads.
# For other databases, this argument is typically not needed.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} # Specific to SQLite
)

# --- SQLAlchemy Session Configuration ---
# SessionLocal is a factory for creating new database sessions.
# A session is a workspace for all database operations (queries, commits, etc.).
# - autocommit=False: Transactions are not automatically committed. You must explicitly call `db.commit()`.
# - autoflush=False: Changes are not automatically flushed to the database before queries.
#                    You might need to call `db.flush()` manually in certain scenarios or before commit.
# - bind=engine: Associates this session factory with our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Declarative Base for Models ---
# Base is a class from which all SQLAlchemy model (table) classes will inherit.
# It provides the declarative system that maps Python classes to database tables.
# Example:
# from app.core.database import Base
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     # ... other columns
Base = declarative_base()

# --- Dependency for FastAPI Endpoints ---
# This function can be used as a dependency in FastAPI path operations
# to get a database session. It ensures that the session is properly
# created before the request and closed after the request, even if errors occur.
#
# Example usage in an endpoint:
# from fastapi import Depends
# from app.core.database import get_db
#
# @router.get("/items/")
# def read_items(db: Session = Depends(get_db)):
#     # ... use db session ...
#     return items
#
# def get_db():
#     """
#     FastAPI dependency that provides a SQLAlchemy database session.
#     Ensures the session is closed after the request.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Note: The get_db dependency is typically defined in `app.core.dependencies.py`.
# If it's not there, the commented-out code above is a standard implementation.
