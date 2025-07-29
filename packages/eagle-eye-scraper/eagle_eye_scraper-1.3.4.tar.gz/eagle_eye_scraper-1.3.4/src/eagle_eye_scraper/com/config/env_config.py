import os
from dataclasses import dataclass, asdict


@dataclass
class Config:
    PROJECT_NAME: str = None

    ENABLE_MYSQL: bool = False
    MYSQL_HOST: str = None
    MYSQL_PORT: int = -1
    MYSQL_USER: str = None
    MYSQL_PASSWORD: str = None
    MYSQL_DEFAULT_DATABASE: str = None

    ENABLE_MINIO: bool = False
    MINIO_ENDPOINT: str = None
    MINIO_ACCESS_KEY: str = None
    MINIO_SECRET_KEY: str = None
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = None

    ENABLE_MONGODB: bool = False
    MONGODB_HOST: str = None
    MONGODB_PORT: int = -1
    MONGODB_USER: str = None
    MONGODB_PASSWORD: str = None
    MONGODB_DEFAULT_DB: str = None

    ENABLE_REDIS: bool = False
    REDIS_TYPE: str = None
    REDIS_HOST: str = None
    REDIS_PORT: int = -1
    REDIS_PASSWORD: str = None
    REDIS_DATABASE: int = 0
    REDIS_MAX_CONNECTIONS: int = 32

    ENABLE_PULSAR: bool = False
    PULSAR_URL: str = None

    LOG_LEVEL: str = None
    LOG_PATH: str = None

    def __post_init__(self):
        for name, field_type in self.__annotations__.items():
            value = getattr(self, name)
            if issubclass(field_type, bool):
                value = bool(value in {'True', 'TRUE', 'true', '1'})
            else:
                value = field_type(value)
            setattr(self, name, value)

CONFIG = Config(**{k: v for k, v in os.environ.items() if k in Config.__annotations__})
print(asdict(CONFIG))
