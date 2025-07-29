from pydantic import BaseSettings
from yarl import URL


class LocationConfig(BaseSettings):

    host: str = 'location'
    port: int = 8000
    api_path: str = 'location'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    class Config:
        env_prefix = "LOCATION_"

