import miniopy_async

from .config import MinioConfig

config = MinioConfig()

client = miniopy_async.Minio(
    config.url,
    access_key=config.access_key,
    secret_key=config.secret_key,
    region=config.region,
    secure=False,
)