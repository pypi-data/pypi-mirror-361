from pydantic import BaseSettings


class DbConfig(BaseSettings):

    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    host: str = "postgres"
    port: int = 5432
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    driver: str = "postgresql+asyncpg"


    @property
    def url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    class Config:
        env_prefix = "POSTGRES_"