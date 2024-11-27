from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str  # Will be read from environment variables

    class Config:
        env_file = ".env"  # Specify the environment file
        env_file_encoding = "utf-8"  # Set encoding for the .env file

# Load settings
settings = Settings()

