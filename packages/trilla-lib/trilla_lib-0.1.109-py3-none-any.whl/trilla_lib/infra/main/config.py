import os

from pydantic import BaseSettings
from yarl import URL


class MainConfig(BaseSettings):

    host: str = 'main_app'
    port: int = 8000
    ext_port: int = 47301
    api_path: str = 'main'

    @property
    def url(self) -> URL:
        return URL.build(scheme='http', host=self.host, port=self.port) / self.api_path

    @property
    def auth_url(self) -> URL:
        domain_name = os.getenv("DOMAIN_NAME")
        deploy_env = os.getenv("DEPLOY_ENV", "local")
        scheme = 'https' if deploy_env != "local" else 'http'
        port = 443 if deploy_env != "local" else self.ext_port
        return URL.build(scheme=scheme, host=domain_name, port=port) / "main/oauth/token"


    class Config:
        env_prefix = "MAIN_"

