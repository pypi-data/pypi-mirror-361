from pydantic import BaseSettings


class DebeziumConfig(BaseSettings):

    host: str = 'debezium'
    port: int = 8083

    class Config:
        env_prefix = "DEBEZIUM_"