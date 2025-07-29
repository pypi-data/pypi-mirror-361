from pydantic import BaseSettings
from yarl import URL


class ReelConfig(BaseSettings):

    host: str = 'reel'
    port: int = 8188
    api_path: str = 'reel'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    class Config:
        env_prefix = "REEL_"

