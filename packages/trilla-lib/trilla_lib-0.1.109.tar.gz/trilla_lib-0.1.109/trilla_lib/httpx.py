from httpx import AsyncClient
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from httpx import AsyncHTTPTransport

HTTPXClientInstrumentor().instrument()


def get_async_client(**kwargs) -> AsyncClient:

    return AsyncClient(
        transport=kwargs.pop("transport", AsyncHTTPTransport(retries=5)),
        timeout=kwargs.pop("timeout", 30),
        **kwargs
    )

