from daily_users_api.models import User


class SideEffectException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class TestUserCreate:

    def test_create_user_no_email(self, db, client):

        data = {
            "email": "",
            "password": "admin"
        }

        res = client.post("/api/v1/users", json=data)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["email"][0] == "Field cannot be empty"

    def test_create_user_no_password(self, db, client):

        data = {
            "email": "ciao@ciao.it",
            "password": ""
        }

        res = client.post("/api/v1/users", json=data)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["password"][0] == "Password must not be empty"

    def test_create_user_success(self, db, client):

        data = {
            "email": "test@user.com",
            "password": "test"
        }

        res = client.post("/api/v1/users", json=data)
        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json["message"] == "user created"

        user = User.get_user(res_json["user"]["id"])

        assert user
        assert user.activation_code != 0
        assert user.activation_code_expiration
        assert user.is_active is False
        assert user.email == data["email"]
        assert user.check_password(data["password"])


class TestUserActivation:

    def test_activate_user_success(self, db, client, unactive_user, unactive_user_headers):

        assert unactive_user.is_active is False

        data = {
            "activation_code": unactive_user.activation_code
        }

        res = client.post("/api/v1/users/activate", json=data, headers=unactive_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == 'user activated'

        user = User.get_user(unactive_user.id)

        assert user.is_active
        assert user.activation_code is None
        assert user.activation_code_expiration is None

    def test_activate_user_wrong_code_format(self, db, client, unactive_user, unactive_user_headers):

        assert unactive_user.is_active is False

        data = {
            "activation_code": "ginopaperino"
        }

        res = client.post("/api/v1/users/activate", json=data, headers=unactive_user_headers)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["activation_code"][0] == 'Not a valid integer.'


class TestUserGetMe:

    def test_get_users_get_me(self, db, client, base_user, base_user_headers):
        res = client.get(
            "/api/v1/users/me",
            headers=base_user_headers
        )

        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json["id"] == base_user.id
        assert res_json["email"] == base_user.email
        assert "password" not in res_json
