from typing import Optional
from pydantic import BaseSettings, Field



class SentryConfig(BaseSettings):

    dsn: str = Field(default='https://some-dsn.ru', description="DSN для подключения к Sentry")
    environment: str = Field(default="dev", description="Окружение (dev, test, prod)", env="DEPLOY_ENV")
    release: Optional[str] = Field(default="0.1.0", description="Версия приложения")
    traces_sample_rate: float = Field(default=1.0, description="Процент запросов для трейсинга (0.0 - 1.0)")
    debug: bool = False
    enabled: bool = True

    class Config:
        env_prefix = "SENTRY_"

sentry_config = SentryConfig()