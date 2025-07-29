from pydantic import BaseSettings
from yarl import URL


class OnlineConfig(BaseSettings):

    host: str = 'online'
    port: int = 8000
    api_path: str = 'online'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    class Config:
        env_prefix = "ONLINE_"

