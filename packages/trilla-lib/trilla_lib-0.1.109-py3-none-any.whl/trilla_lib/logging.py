import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from pythonjsonlogger.json import JsonFormatter
from trilla_lib.contextvars import http_request

class HttpRequestFilter(logging.Filter):

    @staticmethod
    def client_ip_from(request):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host


    def filter(self, record: logging.LogRecord) -> bool:

        req = http_request.get()
        http_method = req.method if req else None
        url_path = req.url.path if req else None
        client_ip = HttpRequestFilter.client_ip_from(req) if req else None

        record.client_ip = client_ip
        record.http_method = http_method
        record.url_path = url_path

        return True


def setup_logging():

    logger = logging.getLogger()
    LoggingInstrumentor().instrument(set_logging_format=True)

    logger.setLevel(logging.INFO)
    logger.handlers = []

    handler = logging.StreamHandler()
    formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(HttpRequestFilter())
    logger.addHandler(handler)

    # logger.propagate = True

