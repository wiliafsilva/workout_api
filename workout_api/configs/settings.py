from pydantic import Field
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = Field(default='postgresql+asyncpg://workout:workout@localhost/workout')


settings = Settings()