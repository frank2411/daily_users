from flask import request, g
from flask_restful import Resource
from marshmallow import ValidationError

from daily_users_api.decorators import check_basicauth_header, authenticate_user, partial_authenticate_user
# from daily_users_api.decorators import redirect_if_not_admin
from daily_users_api.models import User

from daily_users_api.api.schemas import (
    UserSchema, UserGetMeSchema,
    ChangePasswordSchema, RequestResetPasswordSchema, ResetPasswordSchema
)


# class UserDetailResource(Resource):

#     method_decorators = [redirect_if_not_admin, authenticate_user, check_bearer_token]

#     auto_update_fields = ['email', 'password', "role", "is_active"]

#     def get(self, user_id):
#         schema = UserSchema(exclude=['password'])
#         user = User.get_user(user_id, g.current_user)
#         return {'user': schema.dump(user)}

#     def patch(self, user_id):
#         user = User.get_user(user_id, g.current_user)
#         schema = UserSchema(partial=True, instance=user)

#         # If I'm modifying myself so email and password are excluded
#         # this way can track this change separately
#         if user.id == g.current_user.id and user.role.value != "superadmin":
#             schema = UserSchema(
#                 partial=True, exclude=self.auto_update_fields, instance=user)

#         try:
#             user = schema.load(request.json)
#         except ValidationError as err:
#             return err.messages, 422

#         user.save()
#         return {'message': 'user updated', 'user': schema.dump(user)}

#     @redirect_if_not_superadmin
#     def delete(self, user_id):
#         user = User.get_user(user_id, g.current_user)
#         user.delete()
#         return {'message': 'user deleted'}


class UserListResource(Resource):
    """Creation and get_all"""

    # @redirect_if_not_admin
    # def get(self):
    #     schema = UserSchema(many=True, exclude=['password'])
    #     users = User.get_users(g.current_user)
    #     return {"users": schema.dump(users)}

    def post(self):
        try:
            schema = UserSchema(is_creation=True)
            user = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        user.generate_activation_code()
        user.save()

        print(f"Generated code: {user.activation_code} and sended via email.")

        return {'message': 'user created', 'user': schema.dump(user)}, 201


class UserActivationResource(Resource):

    method_decorators = [partial_authenticate_user, check_basicauth_header]

    def post(self):
        pass


class UserGetMeResource(Resource):

    method_decorators = [authenticate_user, check_basicauth_header]

    def get(self):
        schema = UserGetMeSchema()
        return schema.dump(g.current_user)


class UserChangePasswordResource(Resource):
    method_decorators = [authenticate_user, check_basicauth_header]

    def post(self):
        schema = ChangePasswordSchema()
        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {'message': 'password updated'}, 201


class UserRequestPasswordReset(Resource):

    def get(self, token):
        User.validate_temporary_token(token)
        return {'message': 'token valid'}, 200

    def post(self):
        schema = RequestResetPasswordSchema()
        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {'message': 'Request sended'}, 200

    def patch(self, token):
        user = User.validate_temporary_token(token)
        schema = ResetPasswordSchema(instance=user)

        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {'message': 'Passwod reset ok'}, 200
