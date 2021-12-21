from flask import request, g
from flask_restful import Resource
from marshmallow import ValidationError

from daily_users_api.decorators import check_basicauth_header, authenticate_user, partial_authenticate_user
from daily_users_api.models import User

from daily_users_api.api.schemas import (
    UserSchema, UserGetMeSchema, ChangePasswordSchema,
    RequestResetPasswordSchema, ResetPasswordSchema,
    UserCodeValidationSchema, UserUpdateSchema
)


class UserDetailResource(Resource):

    method_decorators = [authenticate_user, check_basicauth_header]

    auto_update_fields = ['email', 'password', "is_active"]

    def get(self, user_id):
        schema = UserSchema()
        user = User.get_user(user_id)
        return {'user': schema.dump(user)}

    def patch(self, user_id):
        user = User.get_user(user_id)
        schema = UserUpdateSchema(partial=True, instance=user)

        # If I'm modifying myself so email and password are excluded
        # this way can track this change separately
        if user.id == g.current_user.id:
            schema = UserUpdateSchema(partial=True, exclude=self.auto_update_fields, instance=user)

        try:
            user = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        user.save()
        return {'message': 'user updated', 'user': schema.dump(user)}

    def delete(self, user_id):
        user = User.get_user(user_id)
        user.delete()
        return {'message': 'user deleted'}


class UserListResource(Resource):
    """Creation and get_all"""

    @check_basicauth_header
    @authenticate_user
    def get(self):
        schema = UserSchema(many=True)
        users = User.get_users()
        return {"users": schema.dump(users)}

    def post(self):
        try:
            schema = UserSchema()
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
        try:
            schema = UserCodeValidationSchema()
            validated_data = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        User.activate_user(g.current_user, validated_data["activation_code"])

        return {'message': 'user activated'}, 200


class UserRequestNewCodeResource(Resource):

    method_decorators = [partial_authenticate_user, check_basicauth_header]

    def post(self):
        user = User.get_user(g.current_user.id)

        if user.is_active:
            return {"message": "Account has already been activated."}, 400

        user.generate_activation_code()
        user.save()

        print(f"Generated code: {user.activation_code} and sended via email.")

        return {'message': 'code regenerated', 'code': user.activation_code}, 200


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
