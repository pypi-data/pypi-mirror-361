from contextvars import ContextVar

http_request: ContextVar = ContextVar('request', default=None)
