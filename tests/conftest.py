import uuid
import pytest
import base64

from daily_users_api.models import User

from daily_users_api.app import create_app
from daily_users_api.models import db as rawdb

# from datetime import datetime
# from datetime import timedelta


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        rawdb.init_db()

        yield rawdb

        rawdb.session.close()
        rawdb.drop_db()


@pytest.fixture
def base_user(db):
    user = User(
        email="testuser@email.com",
        password="test",
        is_active=True,
    )

    user.save()

    return user


@pytest.fixture
def base_user_token(base_user):
    to_tokenize_string = f"{base_user.email}:test".encode("utf-8")
    return base64.b64encode(to_tokenize_string).decode("utf-8")


@pytest.fixture
def base_user_headers(base_user_token):
    headers = {
        "content-type": "application/json",
        "authorization": f"Basic {base_user_token}",
    }

    return headers


@pytest.fixture
def reset_password_user(db):
    user = User(
        email="testuser@email.com",
        password="test",
        is_active=True,
        temporary_token=uuid.uuid4(),
    )

    user.save()

    return user


@pytest.fixture
def reset_password_admin_user(db):
    user = User(
        email="testuser@email.com",
        password="test",
        is_active=True,
        role="admin",
        temporary_token=uuid.uuid4(),
    )

    user.save()

    return user


@pytest.fixture
def base_user_deactivated(db):

    user = User(
        email="testuser_deactivated@email.com",
        password="test",
        is_active=False
    )

    user.save()

    return user


@pytest.fixture
def generic_headers():

    headers = {
        "content-type": "application/json",
        "authorization": "Basic 123123123123",
    }

    return headers
