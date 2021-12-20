from marshmallow import ValidationError


def base_validate_empty_string(schema, value):
    if not value:
        # check needed for empty string password because our lib doesn't validate it
        raise ValidationError(schema.error_messages["value_is_empty"])


def base_validate_empty_int(schema, value):  # pragma: no cover
    if not value:
        # check needed for empty string password because our lib doesn't validate it
        raise ValidationError(schema.error_messages["value_is_empty"])


def base_validate_password(schema, value, user=None):
    if not value:
        # check needed for empty string password because our lib doesn't validate it
        raise ValidationError(schema.error_messages["password_not_provided"])
