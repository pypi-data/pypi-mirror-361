from pydantic import BaseSettings
from yarl import URL


class CentrifugoConfig(BaseSettings):

    host: str = 'centrifugo'
    port: int = 8000
    api_key: str = 'API_KEY'
    namespace = 'namespace'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / 'api'

    class Config:
        env_prefix = "CENTRIFUGO_"

