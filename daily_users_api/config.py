import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    ENV = os.getenv('FLASK_ENV')
    SECRET_KEY = os.getenv('SECRET_KEY', "localkey")


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    DAILY_USERS_DB_ENGINE = os.getenv("DAILY_USERS_DB_ENGINE")
    DAILY_USERS_DB_USER = os.getenv("DAILY_USERS_DB_USER")
    DAILY_USERS_DB_PASSWORD = os.getenv("DAILY_USERS_DB_PASSWORD")
    DAILY_USERS_DB_HOST = os.getenv("DAILY_USERS_DB_HOST")
    DAILY_USERS_DB_PORT = os.getenv("DAILY_USERS_DB_PORT")
    DAILY_USERS_DB_NAME = os.getenv("DAILY_USERS_DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f'{DAILY_USERS_DB_ENGINE}://{DAILY_USERS_DB_USER}:'
        f'{DAILY_USERS_DB_PASSWORD}@{DAILY_USERS_DB_HOST}:'
        f'{DAILY_USERS_DB_PORT}/{DAILY_USERS_DB_NAME}'
    )


class DevelopConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DAILY_USERS_DB_ENGINE = os.getenv("DAILY_USERS_DB_ENGINE")
    DAILY_USERS_DB_USER = os.getenv("DAILY_USERS_DB_USER")
    DAILY_USERS_DB_PASSWORD = os.getenv("DAILY_USERS_DB_PASSWORD")
    DAILY_USERS_DB_HOST = os.getenv("DAILY_USERS_DB_HOST")
    DAILY_USERS_DB_PORT = os.getenv("DAILY_USERS_DB_PORT")
    DAILY_USERS_DB_NAME = os.getenv("DAILY_USERS_DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f'{DAILY_USERS_DB_ENGINE}://{DAILY_USERS_DB_USER}:'
        f'{DAILY_USERS_DB_PASSWORD}@{DAILY_USERS_DB_HOST}:'
        f'{DAILY_USERS_DB_PORT}/{DAILY_USERS_DB_NAME}'
    )


class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DAILY_USERS_DB_ENGINE = os.getenv("DAILY_USERS_DB_ENGINE", "postgresql")
    DAILY_USERS_DB_USER = os.getenv("DAILY_USERS_DB_USER", "postgres")
    DAILY_USERS_DB_PASSWORD = os.getenv("DAILY_USERS_DB_PASSWORD", "admin")
    DAILY_USERS_DB_HOST = os.getenv("DAILY_USERS_DB_HOST", "db")
    DAILY_USERS_DB_PORT = os.getenv("DAILY_USERS_DB_PORT", "5432")
    DAILY_USERS_DB_NAME = os.getenv("DAILY_USERS_DB_NAME", "daily_users")

    SQLALCHEMY_DATABASE_URI = (
        f'{DAILY_USERS_DB_ENGINE}://{DAILY_USERS_DB_USER}:'
        f'{DAILY_USERS_DB_PASSWORD}@{DAILY_USERS_DB_HOST}:'
        f'{DAILY_USERS_DB_PORT}/{DAILY_USERS_DB_NAME}'
    )


class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True

    DAILY_USERS_DB_ENGINE = os.getenv("TEST_DB_ENGINE", "postgresql")
    DAILY_USERS_DB_USER = os.getenv("TEST_DB_USER", "postgres")
    DAILY_USERS_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "admin")
    DAILY_USERS_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
    DAILY_USERS_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
    DAILY_USERS_DB_NAME = os.getenv("TEST_DB_NAME", "daily_users_test")

    SQLALCHEMY_DATABASE_URI = (
        f'{DAILY_USERS_DB_ENGINE}://{DAILY_USERS_DB_USER}:'
        f'{DAILY_USERS_DB_PASSWORD}@{DAILY_USERS_DB_HOST}:'
        f'{DAILY_USERS_DB_PORT}/{DAILY_USERS_DB_NAME}'
    )
