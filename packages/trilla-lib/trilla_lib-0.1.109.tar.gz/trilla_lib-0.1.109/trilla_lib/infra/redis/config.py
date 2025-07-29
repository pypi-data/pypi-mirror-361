from pydantic import BaseSettings
from yarl import URL


class RedisConfig(BaseSettings):

    host: str = 'redis'
    port: int = 6379
    db: int = 0

    @property
    def url(self):
        return URL.build(scheme="redis", host=self.host, port=self.port) / str(self.db)

    class Config:
        env_prefix = "REDIS_"