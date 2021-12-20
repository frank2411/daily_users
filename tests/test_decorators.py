import pytest

from unittest.mock import Mock, patch
from daily_users_api.decorators import check_basicauth_header
from daily_users_api.decorators import authenticate_user


class SideEffectException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class TestAuthorizationDecorators:

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_success(self, abort_mock, request_mock, generic_headers):
        fn = Mock()
        fn.return_value = "returned"

        request_mock.headers = generic_headers

        dec = check_basicauth_header(fn)
        ret = dec()

        assert ret == "returned"

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_malformed_auth_header_no_bearer(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "123123123123",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No Bearer")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_basicauth_header(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No Bearer"

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_malformed_auth_header_no_token(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "Basic",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No Token")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_basicauth_header(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No Token"

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_malformed_auth_header_uncorrect_bearer(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "Bas 123123123123",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("Malformed Basic")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_basicauth_header(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "Malformed Basic"

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_no_auth_header(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No auth header")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_basicauth_header(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No auth header"

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_auth_decorator_no_correct_base64(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "Basic 1231231313123"
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No correct base64")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_basicauth_header(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No correct base64"


class TestAuthenticateDecorator:

    @patch('daily_users_api.decorators.request', spec={})
    @patch('daily_users_api.decorators.abort')
    def test_authenticate_user_valid(self, abort_mock, request_mock, base_user_headers):
        fn = Mock()
        fn.return_value = "returned"
        request_mock.headers = base_user_headers

        dec = authenticate_user(fn)
        ret = dec()

        assert ret == "returned"

    # @patch('daily_users_api.decorators.request', spec={})
    # @patch('daily_users_api.decorators.User.set_current_user')
    # def test_authenticate_user_aborted(self, token_mock, request_mock, generic_headers):
    #     headers = {
    #         "content-type": "application/json",
    #         "authorization": f"Basic {access_token}",
    #     }

    #     fn = Mock()
    #     fn.return_value = "returned"
    #     request_mock.headers = headers
    #     token_mock.side_effect = SideEffectException("Something went wrong")

    #     with pytest.raises(SideEffectException) as httperror:
    #         dec = authenticate_user(fn)
    #         dec()

    #     assert httperror.value
    #     assert httperror.value.message == "Something went wrong"
