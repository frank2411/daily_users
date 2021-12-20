from daily_users_api.models import User


class TestResetPassword:

    def test_request_reset_password_no_email(self, db, client):
        data = {"email": ""}
        resp = client.post('/api/v1/users/reset-password', json=data)
        assert resp.status_code == 422

    def test_request_reset_password_no_user(self, db, client):
        json = {"email": "fake@user.it"}
        resp = client.post('/api/v1/users/reset-password', json=json)
        assert resp.status_code == 200

    def test_request_reset_password_method_not_allowed_post(self, db, client):
        resp = client.post('/api/v1/users/reset-password/12123123120')
        assert resp.status_code == 405

    def test_request_reset_password_patch_method_not_authorized(self, db, client):
        resp = client.patch('/api/v1/users/reset-password/')
        assert resp.status_code == 405

    def test_request_reset_password_patch_method_not_found(self, db, client):
        resp = client.patch('/api/v1/users/reset-password/123123')
        assert resp.status_code == 404

    def test_request_reset_password_200(self, app, client, base_user):
        check_id = base_user.id
        # check_email = base_user.email
        json = {"email": base_user.email}
        resp = client.post('/api/v1/users/reset-password', json=json)

        check_user = User.query.get(check_id)

        assert resp.status_code == 200
        assert check_user.temporary_token is not None

    def test_get_reset_password_token_not_valid(self, client, db, reset_password_user):
        resp = client.get('/api/v1/users/reset-password/123123123213',)
        assert resp.status_code == 404

    def test_get_reset_password_token_valid(self, client, db, reset_password_user):
        resp = client.get(f'/api/v1/users/reset-password/{reset_password_user.temporary_token}',)
        assert resp.status_code == 200

    def test_reset_password_token_not_valid(self, client, db, reset_password_user):
        json = {"password": "test_valid"}
        resp = client.patch('/api/v1/users/reset-password/12312312312123', json=json)
        assert resp.status_code == 404

    def test_reset_password_password_not_valid(self, client, db, reset_password_user):
        json = {"password": ""}
        resp = client.patch(f'/api/v1/users/reset-password/{reset_password_user.temporary_token}', json=json)
        assert resp.status_code == 422

    def test_reset_password_valid(self, client, db, reset_password_user):
        check_id = reset_password_user.id
        last_password_update = reset_password_user.last_password_update

        json = {"password": "test_valid@Test10"}
        resp = client.patch(f'/api/v1/users/reset-password/{reset_password_user.temporary_token}', json=json)

        check_user = User.query.get(check_id)
        assert resp.status_code == 200
        assert check_user.check_password("test_valid@Test10")
        assert check_user.last_password_update != last_password_update


# class TestUserChangePasswordActions:

#     def test_user_change_password_fail_no_data(self, client, db, admin, admin_headers):
#         data = {}
#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         errors = response.get_json()

#         assert len(errors) == 3
#         assert response.status_code == 422

#     def test_user_change_password_fail_no_old_password(self, client, db, admin, admin_headers):
#         data = {
#             "old_password": "",
#             "new_password": "test_valid@Test10",
#             "new_password_confirm": "test_valid@Test10",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         errors = response.get_json()

#         assert "old_password" in errors.keys()
#         assert "Old Password must not be empty" in errors["old_password"]
#         assert len(errors) == 1
#         assert response.status_code == 422

#     def test_user_change_password_fail_wrong_old_password(self, client, db, admin, admin_headers):
#         data = {
#             "old_password": "tes",
#             "new_password": "test_valid@Test10",
#             "new_password_confirm": "test_valid@Test10",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         errors = response.get_json()

#         assert "old_password" in errors.keys()
#         assert "Old password doesn't exists" in errors["old_password"]
#         assert len(errors) == 1
#         assert response.status_code == 422

#     def test_user_change_password_fail_password_mismatch(self, client, db, admin, admin_headers):
#         data = {
#             "old_password": "test",
#             "new_password": "test_valid@Test10",
#             "new_password_confirm": "pass",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         errors = response.get_json()

#         assert "passwords" in errors.keys()
#         assert "Passwords are not the same" in errors["passwords"]
#         assert len(errors) == 1
#         assert response.status_code == 422

#     def test_user_change_password_fail_empty_new_password(self, client, db, admin, admin_headers):
#         data = {
#             "old_password": "test",
#             "new_password": "",
#             "new_password_confirm": "",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         errors = response.get_json()

#         assert "new_password" in errors.keys()
#         assert "Password must not be empty" in errors["new_password"]
#         assert len(errors) == 1
#         assert response.status_code == 422

#     def test_user_change_password_201(self, client, db, admin, admin_headers):
#         user_id = admin.id
#         last_password_update = admin.last_password_update

#         data = {
#             "old_password": "test",
#             "new_password": "test_valid@Test10",
#             "new_password_confirm": "test_valid@Test10",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=admin_headers,
#             json=data
#         )

#         result = response.get_json()

#         updated_user = User.query.get(user_id)

#         assert updated_user.last_password_update != last_password_update
#         assert updated_user.id == user_id
#         assert "message" in result.keys()
#         assert "password updated" in result["message"]
#         assert updated_user.check_password("test_valid@Test10")
#         assert response.status_code == 201

#     def test_base_user_change_password_201(self, client, db, base_user, base_user_headers):
#         user_id = base_user.id
#         last_password_update = base_user.last_password_update

#         data = {
#             "old_password": "test",
#             "new_password": "test_valid@Test10",
#             "new_password_confirm": "test_valid@Test10",
#         }

#         response = client.post(
#             '/api/v1/users/change-password',
#             headers=base_user_headers,
#             json=data
#         )

#         result = response.get_json()

#         updated_user = User.query.get(user_id)

#         assert updated_user.last_password_update != last_password_update
#         assert updated_user.id == user_id
#         assert "message" in result.keys()
#         assert "password updated" in result["message"]
#         assert updated_user.check_password("test_valid@Test10")
#         assert response.status_code == 201
