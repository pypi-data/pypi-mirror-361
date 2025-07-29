from pydantic import BaseSettings, Field


class JwtConfig(BaseSettings):
    """JWT Settings"""

    algorithm: str = 'HS256'
    secret: str = Field(min_length=64, max_length=64, default='secret')
    access_ttl: int = 30
    refresh_ttl: int = 10080

    class Config:
        env_prefix = "JWT_"