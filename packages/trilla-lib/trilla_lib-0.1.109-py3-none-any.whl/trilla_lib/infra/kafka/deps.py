import json
from aiokafka import AIOKafkaConsumer
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient
from opentelemetry.instrumentation.aiokafka import AIOKafkaInstrumentor

from .config import KafkaConfig

config = KafkaConfig()

AIOKafkaInstrumentor().instrument()


async def get_admin_client(**kwargs):
    return AIOKafkaAdminClient(bootstrap_servers=config.url, **kwargs)

async def get_producer(**kwargs):
    return AIOKafkaProducer(bootstrap_servers=config.url, **kwargs)

async def get_consumer(*topics, **kwargs):
    value_deserializer = kwargs.pop('value_deserializer', lambda v: json.loads(v.decode("utf-8")) if v else None)
    enable_auto_commit = kwargs.pop('enable_auto_commit', False)

    return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=config.url,
            group_id=config.group_id,
            enable_auto_commit=enable_auto_commit,
            value_deserializer=value_deserializer,
            **kwargs
    )

