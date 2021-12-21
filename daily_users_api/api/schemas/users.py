from flask import g

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, Schema, validates_schema
from marshmallow import ValidationError, validates, post_load, post_dump

from .custom_validators import base_validate_empty_string, base_validate_password

from daily_users_api.models import db
from daily_users_api.models import User


class UserSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "password_not_provided": "Password must not be empty",
        "value_is_empty": "Field cannot be empty",
    }

    @validates("email")
    def validate_email(self, value):
        base_validate_empty_string(self, value)

    @validates("password")
    def validate_password(self, value):
        base_validate_password(self, value, user=self.instance)

    @post_dump
    def exclude_password(self, obj, **kwargs):
        del obj["password"]
        return obj

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("is_active", "activation_code", "activation_code_expiration")


class UserUpdateSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "password_not_provided": "Password must not be empty",
        "value_is_empty": "Field cannot be empty",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.original_password = self.instance.password

    @validates("email")
    def validate_email(self, value):
        base_validate_empty_string(self, value)

    @validates("password")
    def validate_password(self, value):
        base_validate_password(self, value, user=self.instance)

    @post_dump
    def exclude_password(self, obj, **kwargs):
        del obj["password"]
        return obj

    @post_load
    def set_new_password(self, instance, **kwargs):
        if self.partial and instance.password != self.original_password:
            instance.password = User.set_password_hash(instance.password)
        return instance

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("activation_code", "activation_code_expiration")


class UserGetMeSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = User
        sqla_session = db.session
        include_relationships = True
        load_instance = True
        exclude = ("password", "is_active", "activation_code", "activation_code_expiration")


class UserCodeValidationSchema(SQLAlchemyAutoSchema):
    activation_code = fields.Integer(required=True)


class ChangePasswordSchema(Schema):
    error_messages = {
        "passwords_mismatch": "Passwords are not the same",
        "old_password_mismatch": "Old password doesn't exists",
        "old_password_not_provided": "Old Password must not be empty",
        "password_not_provided": "Password must not be empty",
        "password_too_short_admin": "Password must not be at least 12 characters long",
        "password_too_short_user": "Password must not be at least 8 characters long",
        "password_format_not_valid": "Password isn't satisfying its structure needs",
    }

    old_password = fields.String(required=True)
    new_password = fields.String(required=True)
    new_password_confirm = fields.String(required=True)

    @validates("old_password")
    def validate_old_password(self, value):
        if not value:
            raise ValidationError(self.error_messages["old_password_not_provided"])

        old_password = value
        password_valid = g.current_user.check_password(old_password)

        if not password_valid:
            raise ValidationError(self.error_messages["old_password_mismatch"])

    @validates("new_password")
    def validate_new_password(self, value):
        base_validate_password(self, value, user=g.current_user)

    @validates_schema
    def validate_new_password_match(self, data, **kwargs):
        if data["new_password"] != data["new_password_confirm"]:
            raise ValidationError(
                self.error_messages["passwords_mismatch"], "passwords"
            )

    @post_load
    def set_new_password(self, data, **kwargs):
        g.current_user.password = User.set_password_hash(data["new_password"])
        g.current_user.save(password_updated=True)


class ResetPasswordSchema(SQLAlchemyAutoSchema):
    error_messages = {
        "password_not_provided": "Password must not be empty",
        "password_too_short_admin": "Password must not be at least 12 characters long",
        "password_too_short_user": "Password must not be at least 8 characters long",
        "password_format_not_valid": "Password isn't satisfying its structure needs",
    }

    password = fields.String(required=True)

    @validates("password")
    def validate_password(self, value):
        base_validate_password(self, value, user=self.instance)

    @post_load
    def set_new_password(self, data, **kwargs):
        self.instance.password = User.set_password_hash(data["password"])
        self.instance.save(password_updated=True)

    class Meta:
        model = User
        fields = ("password",)


class RequestResetPasswordSchema(Schema):

    email = fields.Email(required=True)

    class Meta:
        fields = ("email",)

    @post_load
    def create_temporary_token_and_send_email(self, data, **kwargs):
        user = User.get_user_for_reset_password(data.get("email"))
        if not user:  # Fake successful password request
            return

        user.create_temporary_token()

        # @TODO send mail logic HERE (external service like the one for the activation code)
        print("Mail sendend")
