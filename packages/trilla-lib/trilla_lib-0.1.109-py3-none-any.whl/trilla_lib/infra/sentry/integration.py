import sentry_sdk
from typing import TypeAlias
from typing import Literal
from trilla_lib.infra.sentry.settings import sentry_config


Plugins: TypeAlias = set[Literal['fastapi', 'sqlalchemy', 'redis', 'celery']]

def _get_integrations(plugins: Plugins):

    result = []

    if 'fastapi' in plugins:
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        result.append(FastApiIntegration())

    if 'sqlalchemy' in plugins:
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        result.append(SqlalchemyIntegration())

    if 'redis' in plugins:
        from sentry_sdk.integrations.redis import RedisIntegration
        result.append(RedisIntegration())

    if 'celery' in plugins:
        from sentry_sdk.integrations.celery import CeleryIntegration
        result.append(CeleryIntegration())

    return result


def init_sentry(
    plugins: Plugins,
) -> None:

    if not sentry_config.enabled:
        return

    sentry_sdk.init(
        dsn=sentry_config.dsn,
        send_default_pii=True,
        environment=sentry_config.environment,
        release=sentry_config.release,
        traces_sample_rate=sentry_config.traces_sample_rate,
        integrations=_get_integrations(plugins),
        debug=sentry_config.debug,
        instrumenter="otel",
    )
