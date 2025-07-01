# settings.py
# Configuration settings for the application.
# This file includes secrets, algorithm specifications, token expiry times, and logging setup.
# It is crucial to manage secrets securely, potentially using environment variables or a vault in production.

import logging
import os # Recommended for accessing environment variables

# --- Security and JWT Settings ---

# Secret key for encoding JWT access tokens.
# IMPORTANT: This should be a strong, unique key and ideally loaded from environment variables in production.
# Example: SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
SECRET_KEY = "09027e5d4c40783326cef1ee95c179c7dcaa4c92e90844c1c1958b027546d240"

# Secret key for encoding JWT refresh tokens.
# IMPORTANT: This should also be a strong, unique key and loaded from environment variables.
# Example: REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your-default-refresh-secret-key")
REFRESH_SECRET_KEY = "b92bb176d0c75d87efce31a3f4c472b3648d6e63d4b6a349802f712ba4422489"

# Algorithm used for JWT encoding and decoding. HS256 is a common choice.
ALGORITHM = "HS256"

# Expiration time for access tokens in minutes.
# Current setting: 60 minutes * 24 hours * 7 days = 7 days.
# Consider if this duration is appropriate for your security requirements.
# Shorter lifespans for access tokens are generally more secure, with refresh tokens used for longer sessions.
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Expiration time for refresh tokens in days.
# Current setting: 60 days * 24 hours * 7 days = This seems to be an error, likely meant REFRESH_TOKEN_EXPIRE_DAYS = 7
# Corrected to REFRESH_TOKEN_EXPIRE_DAYS = 7 for 7 days, adjust as needed.
# Refresh tokens typically have a longer lifespan than access tokens.
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days, corrected from 60*24*7 which would be 10080 minutes or 7 days.
                               # If a different value like 30 days was intended, it should be set directly as 30.

# --- Logging Configuration ---

# Basic logging setup.
# This configures the root logger. For more granular control, configure specific loggers.
# Consider using a more structured logging format (e.g., JSON) for easier parsing in production.
# Also, consider environment-specific logging levels (e.g., DEBUG in development, INFO or WARNING in production).
logging.basicConfig(
    level=logging.INFO,  # Default logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

# Get a logger instance for the current module.
# This is a common practice to allow module-specific logging.
logger = logging.getLogger(__name__)

# Example: How to use the logger in other modules:
# from app.core.settings import logger
# logger.info("This is an info message.")
# logger.error("This is an error message.")

# --- Environment Variable Example (Best Practice) ---
# It's highly recommended to load sensitive data and configurations
# that vary between environments (dev, staging, prod) from environment variables.
#
# from dotenv import load_dotenv
# load_dotenv() # Loads variables from .env file for local development
#
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default.db")
# API_KEY = os.getenv("SOME_API_KEY")
#
# if not API_KEY:
#     logger.warning("SOME_API_KEY is not set in environment variables.")
