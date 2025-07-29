from pydantic import BaseSettings, Field


class MinioConfig(BaseSettings):
    """Minio config."""

    host: str = "minio"
    port: int = 9000
    access_key: str = Field(default="minio-root", env="MINIO_ROOT_USER")
    secret_key: str = Field(default="minio-root", env="MINIO_ROOT_PASSWORD")
    region: str = Field(default="eu-north-1")

    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    class Config:
        env_prefix = "MINIO_"
