from cent import Client
from .config import CentrifugoConfig

config = CentrifugoConfig()

client = Client(
    config.url,
    api_key=config.api_key,
    timeout=1,
)
