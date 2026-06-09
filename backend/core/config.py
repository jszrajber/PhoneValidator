from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str

    NUM_API_KEY: str

    REDIS_HOST: str

    @property
    def DATABASE_URL(self) -> str:
        """
        Returns valid db url.
        Dynamically assembles the async database connection string 
        using individual PostgreSQL credentials.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Returns valid reids url."""
        return f"redis://{self.REDIS_HOST}:6379"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
