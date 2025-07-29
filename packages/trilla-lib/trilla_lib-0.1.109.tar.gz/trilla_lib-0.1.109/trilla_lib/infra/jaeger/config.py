from pydantic import BaseSettings


class JaegerConfig(BaseSettings):

    service_name: str = "my-fastapi-app"
    agent_host: str = "localhost"
    agent_port: int = 6831
    sampling_rate: float = 1.0
    enabled: bool = False

    class Config:
        env_prefix = "JAEGER_"


jaeger_config = JaegerConfig()

