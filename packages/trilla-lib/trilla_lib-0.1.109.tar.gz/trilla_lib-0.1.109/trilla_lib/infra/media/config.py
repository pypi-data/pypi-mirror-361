from pydantic import BaseSettings
from yarl import URL


class MediaConfig(BaseSettings):

    host: str = 'media_service'
    port: int = 8000
    api_path: str = 'media'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    @property
    def image_upload_url(self) -> URL:
        return self.url / 'im'

    class Config:
        env_prefix = "MEDIA_"

