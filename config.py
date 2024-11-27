from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str  # Will be read from environment variables

    class Config:
        env_file = ".env"  # Specify the environment file
        env_file_encoding = "utf-8"  # Set encoding for the .env file

# Load settings
settings = Settings()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
Base = declarative_base()
