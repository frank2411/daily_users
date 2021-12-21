from daily_users_api.models import User
from sqlalchemy.sql.expression import select


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


class TestUsersGet:

    def test_get_list_of_users(self, db, client, unactive_user, base_user, base_user_headers):

        res = client.get("/api/v1/users", headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert len(res_json["users"]) == 2


class TestUserDelete:

    def test_delete_user_not_found(self, db, client, unactive_user, base_user, base_user_headers):

        res = client.delete("/api/v1/users/123123", headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "User not found"

    def test_delete_user_success(self, db, client, unactive_user, base_user, base_user_headers):

        to_check_id = unactive_user.id

        res = client.delete(f"/api/v1/users/{unactive_user.id}", headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "user deleted"

        user_query = select(User).where(User.id == to_check_id)
        user = db.session.execute(user_query).scalar_one_or_none()

        assert user is None


class TestUserGet:

    def test_get_user_not_found(self, db, client, base_user, base_user_headers):

        res = client.get("/api/v1/users/123123", headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == "User not found"

    def test_get_user_success(self, db, client, unactive_user, base_user, base_user_headers):

        res = client.get(f"/api/v1/users/{unactive_user.id}", headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["user"]["id"] == unactive_user.id 


class TestUserUpdate:

    def test_update_user_success(self, db, client, unactive_user, base_user, base_user_headers):

        assert unactive_user.is_active is False

        data = {
            "is_active": True
        }

        res = client.patch(f"/api/v1/users/{unactive_user.id}", json=data, headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "user updated"
        assert res_json["user"]["is_active"] is True

    def test_update_user_password_update_success(self, db, client, unactive_user, base_user, base_user_headers):

        assert unactive_user.is_active is False

        data = {
            "password": "ciao"
        }

        res = client.patch(f"/api/v1/users/{unactive_user.id}", json=data, headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json["message"] == "user updated"

        user_query = select(User).where(User.id == unactive_user.id)
        user = db.session.execute(user_query).scalar_one_or_none()

        assert user.check_password(data["password"])

    def test_update_user_generic_fail(self, db, client, unactive_user, base_user, base_user_headers):

        assert unactive_user.is_active is False

        data = {
            "is_active": True,
            "email": ""
        }

        res = client.patch(f"/api/v1/users/{unactive_user.id}", json=data, headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["email"][0] == 'Field cannot be empty'

    def test_update_user_is_me_password_update_fail(self, db, client, base_user, base_user_headers):

        data = {
            "password": "1231312"
        }

        res = client.patch(f"/api/v1/users/{base_user.id}", json=data, headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["password"][0] == 'Unknown field.'


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

    def test_activate_user_user_already_active(self, db, client, base_user, base_user_headers):

        assert base_user.is_active is True

        data = {
            "activation_code": 1234
        }

        res = client.post("/api/v1/users/activate", json=data, headers=base_user_headers)
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json["message"] == 'User already active or code not valid.'

    def test_activate_user_wrong_code_format(self, db, client, unactive_user, unactive_user_headers):

        assert unactive_user.is_active is False

        data = {
            "activation_code": "ginopaperino"
        }

        res = client.post("/api/v1/users/activate", json=data, headers=unactive_user_headers)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["activation_code"][0] == 'Not a valid integer.'

    def test_activate_user_code_expired(self, db, client, code_expired_user, code_expired_user_headers):

        assert code_expired_user.is_active is False

        data = {
            "activation_code": code_expired_user.activation_code
        }

        res = client.post("/api/v1/users/activate", json=data, headers=code_expired_user_headers)
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json["message"] == 'Activation code has expired'


class TestCodeResend:

    def test_code_resend_fail_user_already_active(self, db, client, base_user, base_user_headers):
        res = client.post(
            "/api/v1/users/code",
            headers=base_user_headers
        )

        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json["message"] == "Account has already been activated."

    def test_code_resend_success(self, db, client, unactive_user, unactive_user_headers):

        old_code = unactive_user.activation_code
        old_code_expiration = unactive_user.activation_code_expiration

        res = client.post(
            "/api/v1/users/code",
            headers=unactive_user_headers
        )

        res_json = res.get_json()

        user = User.get_user(unactive_user.id)

        assert res.status_code == 200
        assert res_json["message"] == "code regenerated"
        assert old_code != user.activation_code
        assert old_code_expiration != user.activation_code_expiration


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
