from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Global configuration settings for microservices"""
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    RABBITMQ_URL: str = "amqps://guest:guest@rabbitmq:5671/"
    SERVICE_NAME: str = "default-service"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
