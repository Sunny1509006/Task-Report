from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str
    SECRET_KEY: str
    ALGORITHM: str # Or whatever you're using (e.g., RS256)

    class Config:
        env_file = ".env"  # Optional: load from .env if you want

settings = Settings()
