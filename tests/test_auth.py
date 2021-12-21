class TestBasicAuth:

    def test_auth_wrong_credentials_len(self, db, client, wrong_len_token):
        headers = {
            "content-type": "application/json",
            "authorization": f"Basic {wrong_len_token}",
        }

        res = client.get(
            "/api/v1/users/me",
            headers=headers
        )

        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json["message"] == "Bad Credentials"

    def test_auth_nonexistent_username(self, db, client, nonexistent_username_token):
        headers = {
            "content-type": "application/json",
            "authorization": f"Basic {nonexistent_username_token}",
        }

        res = client.get(
            "/api/v1/users/me",
            headers=headers
        )

        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json["message"] == "Bad Credentials"

    def test_auth_wrong_password(self, db, client, base_user, invalid_password_token):
        headers = {
            "content-type": "application/json",
            "authorization": f"Basic {invalid_password_token}",
        }

        res = client.get(
            "/api/v1/users/me",
            headers=headers
        )

        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json["message"] == "Bad Credentials"
