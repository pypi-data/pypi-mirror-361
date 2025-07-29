from pydantic import BaseSettings
from yarl import URL


class FeedConfig(BaseSettings):

    host: str = 'feed'
    port: int = 8000
    api_path: str = 'feed'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    class Config:
        env_prefix = "FEED_"

