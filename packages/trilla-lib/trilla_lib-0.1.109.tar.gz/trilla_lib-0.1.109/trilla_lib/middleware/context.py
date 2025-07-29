from starlette.middleware.base import BaseHTTPMiddleware

from trilla_lib.contextvars import http_request as request_cv


class ContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        request_cv.set(request)
        response = await call_next(request)
        return response
