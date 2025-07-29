from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncIterator
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from trilla_lib.infra.db.config import DbConfig

db_config = DbConfig()

engine = create_async_engine(
    db_config.url,
    echo=db_config.echo,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow,
)

SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(
        engine,
        expire_on_commit=False,
    ) as session:
        try:
            yield session
        except Exception:
            raise
        else:
            await session.commit()