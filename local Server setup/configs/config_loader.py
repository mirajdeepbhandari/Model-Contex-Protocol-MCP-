from pathlib import Path
from dotenv import load_dotenv
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from loguru import logger

# Load environment variables from .env file
load_dotenv(dotenv_path=Path("configs/dev.env"))

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    SERVER_NAME: str = Field(..., description="Name of the server")
    VERSION: str = Field(..., description="Application version")
    HOST: str = Field(..., description="Server host")
    PORT: int = Field(..., description="Server port")
    EMBEDDINGS_MODEL: str = Field(..., description="Embeddings model")
    GOOGLE_API_KEY: str = Field(..., description="Google API key")
    PINECONE_API_KEY: str = Field(..., description="Pinecone API key")
    INDEX_NAME: str = Field(..., description="Pinecone index name")
    NAME_SPACE: str = Field(..., description="Pinecone namespace")
    VERFIFIED_EMAIL: str = Field(..., description="Verified email address")

    @field_validator("SERVER_NAME", mode="before")
    def preprocess_value(cls, value):
        """Strip and convert string values to uppercase."""
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        return value.strip().upper()


# Instantiate settings
settings = Settings()

logger.success("Application settings loaded successfully:")
for field_name, field_value in settings.model_dump().items():
    logger.info(f"{field_name}: {field_value}")
