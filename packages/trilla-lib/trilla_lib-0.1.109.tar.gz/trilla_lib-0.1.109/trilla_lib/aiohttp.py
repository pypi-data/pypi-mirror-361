from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from aiohttp import ClientSession, ClientTimeout, TCPConnector

AioHttpClientInstrumentor().instrument()

def get_client_session(**kwargs) -> ClientSession:

    timeout = ClientTimeout(total=5)
    connector = TCPConnector(limit=100)

    return ClientSession(
        timeout=kwargs.pop('timeout', timeout),
        connector=kwargs.pop('connector', connector),
        **kwargs,
    )