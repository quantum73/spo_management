import os

import pytest

from app import create_app, db


@pytest.fixture()
def app():
    app = create_app("test")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db_path = app.config.get("SQLALCHEMY_DATABASE_URI").lstrip("sqlite:///")

    os.remove(db_path)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
