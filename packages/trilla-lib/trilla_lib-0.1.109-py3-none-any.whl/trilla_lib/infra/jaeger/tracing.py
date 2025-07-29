import os
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from trilla_lib.infra.jaeger.config import jaeger_config


def init_tracing(fastapi = None):

    if not jaeger_config.enabled:
        return

    provider = TracerProvider(
        resource=Resource.create({
            "service.name": jaeger_config.service_name,
            "deploy.env": os.getenv("DEPLOY_ENV","local"),
        }),
        sampler=TraceIdRatioBased(jaeger_config.sampling_rate),
    )

    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_config.agent_host,
        agent_port=jaeger_config.agent_port,
    )

    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))


    trace.set_tracer_provider(provider)


    if fastapi is not None:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument_app(fastapi)
