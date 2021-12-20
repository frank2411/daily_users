import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, inspect, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import func


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.Model.metadata.create_all(db.get_engine())


@click.command("drop-db")
@with_appcontext
def drop_db_command():
    db.Model.metadata.drop_all(db.get_engine())


class Model:
    __abstract__ = True

    session = None
    query = None

    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def save(self):
        if not self.id:
            db.session.add(self)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        identity = inspect(self).identity

        if identity is None:
            pk = f"(transient {id(self)})"
        else:
            pk = ", ".join(str(value) for value in identity)

        return f"<{type(self).__name__} {pk}>"


class DynamicBindSession(Session):

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def get_bind(self, mapper=None, clause=None):
        """Return the engine or connection for a given model"""

        if self.bind:
            return self.bind

        # Get default engine
        return self.db.get_engine()


class DBConfig:

    def __init__(self, app=None):
        self.engine = None
        self.app = app
        self.session = self.get_session()
        self.model_class = Model
        self.Model = self.make_declarative_base(self.model_class)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.cleanup)
        app.cli.add_command(init_db_command)
        app.cli.add_command(drop_db_command)

    def cleanup(self, resp_or_exc):
        if self.session:
            self.session.remove()
        return resp_or_exc

    def init_db(self):
        self.Model.metadata.create_all(self.get_engine())

    def drop_db(self):
        self.Model.metadata.drop_all(self.get_engine())

    # We must set the engine in the session class. Since we have to wait for the
    # application context to be loaded in order to have the right configs
    def get_engine(self, is_query=True):
        if self.engine:
            return self.engine

        self.engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"], future=True)
        return self.engine

    def get_session(self, bind=None):
        self.session = scoped_session(
            sessionmaker(class_=DynamicBindSession, db=self, bind=None, future=True)
        )
        return self.session

    def make_declarative_base(self, model, metadata=None):
        model = declarative_base(cls=model, name="Model")
        model.session = self.session
        model.query = self.session.query_property()
        return model


db = DBConfig()
