from redis.asyncio import Redis

from trilla_lib.infra.redis.config import RedisConfig
from opentelemetry.instrumentation.redis import RedisInstrumentor

config = RedisConfig()

client = Redis(
    host=config.host,
    port=config.port,
    db=config.db,
    encoding="utf-8",
    decode_responses=True
)

RedisInstrumentor().instrument()

