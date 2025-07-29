from pydantic import BaseSettings
from yarl import URL


class ChatConfig(BaseSettings):

    host: str = 'chat'
    port: int = 8000
    api_path: str = 'chat'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    class Config:
        env_prefix = "CHAT_"

