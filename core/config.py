import os

from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    SENTRY_SDN: str = None
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    ELASTICSEARCH_CLOUD: str = "False"
    ELASTICSEARCH_CLOUD_ID: Optional[
        str
    ] = "fc4cb02e0dfc461cabf401c50b41a44e:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ0NGMxMDY1NzE5NWE0Y2M2OTVhNTRkNWU1M2MzYmYzMiRiNjMxNTFmM2ZlNjM0OTBhOWFkODNhZTcxNzljNjA3YQ=="
    ELASTICSEARCH_USER: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = "3f2GOi7AiHsKjTUXTPF4ISia"
    ELASTICSEARCH_API_KEY: Optional[
        str
    ] = "N0tKMl9JWUJ0TVVqTHl4cnlWU3E6cmtoYVRQX3hSTjJ2OFQwVjRVcVNVZw=="
    ELASTICSEARCH_SCHEME: Optional[str] = "http"
    ELASTICSEARCH_HOST: Optional[str] = "localhost"
    ELASTICSEARCH_PORT: Optional[int] = 9200
    GCS_BUCKET_NAME: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_PRIVATE_KEY_ID: str
    GOOGLE_PRIVATE_KEY: str
    GOOGLE_CLIENT_EMAIL: str
    GOOGLE_CLIENT_EMAIL_ID: str
    GOOGLE_CLIENT_ID: str


class DevelopmentConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASSWORD')}@{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    READER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASSWORD')}@{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    GCS_BUCKET_NAME: str = os.getenv("DEV_GCS_BUCKET_NAME")
    GOOGLE_PROJECT_ID: str = os.getenv("DEV_GOOGLE_PROJECT_ID")
    GOOGLE_PRIVATE_KEY_ID: str = os.getenv("DEV_GOOGLE_PRIVATE_KEY_ID")
    GOOGLE_PRIVATE_KEY: str = os.getenv("DEV_GOOGLE_PRIVATE_KEY")
    GOOGLE_CLIENT_EMAIL: str = os.getenv("DEV_GOOGLE_CLIENT_EMAIL")
    GOOGLE_CLIENT_EMAIL_ID: str = os.getenv("DEV_GOOGLE_CLIENT_EMAIL_ID")
    GOOGLE_CLIENT_ID: str = os.getenv("DEV_GOOGLE_CLIENT_ID")


class LocalConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASSWORD')}@{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    READER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASSWORD')}@{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    GCS_BUCKET_NAME: str = os.getenv("DEV_GCS_BUCKET_NAME")
    GOOGLE_PROJECT_ID: str = os.getenv("DEV_GOOGLE_PROJECT_ID")
    GOOGLE_PRIVATE_KEY_ID: str = os.getenv("DEV_GOOGLE_PRIVATE_KEY_ID")
    GOOGLE_PRIVATE_KEY: str = os.getenv("DEV_GOOGLE_PRIVATE_KEY")
    GOOGLE_CLIENT_EMAIL: str = os.getenv("DEV_GOOGLE_CLIENT_EMAIL")
    GOOGLE_CLIENT_EMAIL_ID: str = os.getenv("DEV_GOOGLE_CLIENT_EMAIL_ID")
    GOOGLE_CLIENT_ID: str = os.getenv("DEV_GOOGLE_CLIENT_ID")


class ProductionConfig(Config):
    ENV: str = "production"
    DEBUG: str = False
    APP_PORT: int = 80
    WRITER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('PROD_DB_USER')}:{os.getenv('PROD_DB_PASSWORD')}@{os.getenv('PROD_DB_HOST')}/{os.getenv('PROD_DB_NAME')}"
    READER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('PROD_DB_USER')}:{os.getenv('PROD_DB_PASSWORD')}@{os.getenv('PROD_DB_HOST')}/{os.getenv('PROD_DB_NAME')}"
    GCS_BUCKET_NAME: str = os.getenv("PROD_GCS_BUCKET_NAME")
    GOOGLE_PROJECT_ID: str = os.getenv("PROD_GOOGLE_PROJECT_ID")
    GOOGLE_PRIVATE_KEY_ID: str = os.getenv("PROD_GOOGLE_PRIVATE_KEY_ID")
    GOOGLE_PRIVATE_KEY: str = os.getenv("PROD_GOOGLE_PRIVATE_KEY")
    GOOGLE_CLIENT_EMAIL: str = os.getenv("PROD_GOOGLE_CLIENT_EMAIL")
    GOOGLE_CLIENT_EMAIL_ID: str = os.getenv("PROD_GOOGLE_CLIENT_EMAIL_ID")
    GOOGLE_CLIENT_ID: str = os.getenv("PROD_GOOGLE_CLIENT_ID")


def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "development": DevelopmentConfig(),
        "local": LocalConfig(),
        "production": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
