from pydantic import BaseSettings


class CassandraConfig(BaseSettings):

    host: str = 'cassandra'
    port: int = 9042
    user: str = 'cassandra'
    password: str = 'cassandra'
    keyspace: str = 'keyspace'
    ssl_certificate: str | None = None

    class Config:
        env_prefix = "CASSANDRA_"