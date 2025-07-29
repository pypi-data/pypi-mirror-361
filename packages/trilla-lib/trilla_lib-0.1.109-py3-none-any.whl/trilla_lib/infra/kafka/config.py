from pydantic import BaseSettings


class KafkaConfig(BaseSettings):
    """Kafka settings"""

    host: str = 'kafka'
    port: int = 29092
    group_id: str = 'some_group'

    num_partitions: int = 1
    replication_factor: int = 1

    notification_topic: str = "notifications"
    location_topic: str = "location"


    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    class Config:
        env_prefix = "KAFKA_"
