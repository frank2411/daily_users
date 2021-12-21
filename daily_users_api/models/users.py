import random
import bcrypt
import uuid
import base64

from datetime import datetime, timedelta

from .db import db

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql.expression import select, true, false

from flask import g

from flask_restful import abort


class User(db.Model):
    """
    Basic user model
    """

    __tablename__ = 'daily_users'
    __repr_attrs__ = ['email']

    id = Column(Integer, primary_key=True)

    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=False)

    last_password_update = Column(DateTime(timezone=True), default=func.current_timestamp())
    last_login_date = Column(DateTime(timezone=True), default=func.current_timestamp())

    # User tokens for password reset and first access
    temporary_token = Column(String(255))
    activation_code = Column(Integer)
    activation_code_expiration = Column(DateTime(timezone=False))

    @staticmethod
    def set_current_user(token, is_active_check=True):

        credentials = base64.b64decode(token).decode("utf-8")
        credentials = credentials.split(":")

        # If len is < 2 it means we don't have the correct format
        if len(credentials) < 2:
            abort(400, message='Bad Credentials')

        user_query = select(User).where(User.email == credentials[0])

        # Use this flag for partial user authentication ( still not activated )
        if is_active_check:
            user_query = user_query.where(User.is_active == true())

        user = db.session.execute(user_query).scalar_one_or_none()

        if not user:
            abort(400, message='Bad Credentials')

        password_valid = user.check_password(credentials[1])

        if not password_valid:
            abort(400, message='Bad Credentials')

        user.last_login_date = func.current_timestamp()
        user.save()

        g.current_user = user

        return user

    @staticmethod
    def get_user(user_id):
        user_query = select(User).where(User.id == user_id)
        user = db.session.execute(user_query).scalar_one_or_none()

        if not user:
            abort(404, message='User not found')

        return user

    @staticmethod
    def get_users():
        user_query = select(User)
        users = db.session.execute(user_query).scalars().all()
        return users

    @staticmethod
    def activate_user(current_user, code):
        user_query = select(User).where(
            User.email == g.current_user.email,
            User.is_active == false(),
            User.activation_code == code
        )

        user = db.session.execute(user_query).scalar_one_or_none()

        if not user:
            abort(404, message='User already active or code not valid.')

        # @TODO Check expiration time
        utc_now = datetime.utcnow()

        if utc_now > user.activation_code_expiration:
            abort(400, message='Activation code has expired')

        user.is_active = True
        user.activation_code = None
        user.activation_code_expiration = None
        user.save()

    @staticmethod
    def set_password_hash(raw_password):
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(raw_password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def get_user_for_reset_password(email):
        user_query = select(User).where(User.email == email, User.is_active == true())
        user = db.session.execute(user_query).scalar_one_or_none()
        return user

    @staticmethod
    def validate_temporary_token(token):
        """
        Either validates the token and return the user or it raises a 404 error
        """
        user_query = select(User).where(User.temporary_token == token)
        user = db.session.execute(user_query).scalar_one_or_none()

        if not user:
            abort(404, message='Token not valid')

        return user

    def generate_activation_code(self):
        self.activation_code = random.randint(1000, 9999)
        self.activation_code_expiration = datetime.utcnow() + timedelta(minutes=1)

    def create_temporary_token(self):
        token = uuid.uuid4()
        self.temporary_token = token
        self.save()

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())

    def save(self, password_updated=False):
        if not self.id:
            self.password = User.set_password_hash(self.password)

        if password_updated:
            self.last_password_update = func.current_timestamp()

        self.session.add(self)
        self.session.commit()

    def delete(self):
        self.session.delete(self)
        self.session.commit()
