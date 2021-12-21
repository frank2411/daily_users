from flask import Blueprint
from flask_restful import Api

from .resources import (
    SwaggerView,
    UserDetailResource,
    UserListResource,
    UserGetMeResource,
    UserChangePasswordResource,
    UserRequestPasswordReset,
    UserActivationResource,
    UserRequestNewCodeResource,
)


api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_blueprint)

# Swagger API
api.add_resource(SwaggerView, '/docs', methods=["GET"])

# User apis
api.add_resource(UserDetailResource, '/users/<int:user_id>')
api.add_resource(UserListResource, '/users')
api.add_resource(UserActivationResource, '/users/activate')
api.add_resource(UserRequestNewCodeResource, '/users/code')
api.add_resource(UserGetMeResource, '/users/me')

# Password apis
api.add_resource(UserChangePasswordResource, '/users/change-password')
api.add_resource(UserRequestPasswordReset, '/users/reset-password', methods=["POST"])
api.add_resource(UserRequestPasswordReset, '/users/reset-password/', methods=["POST"], endpoint="dead_endpoint")
api.add_resource(UserRequestPasswordReset, '/users/reset-password/<string:token>', methods=["PATCH", "GET"], endpoint="do_reset")
