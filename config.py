import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', str(uuid.uuid4()))
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', str(uuid.uuid4()))
    STATIC_PATH = os.environ.get('STATIC_PATH', "")
    STATIC_FOLDER = os.environ.get('STATIC_URL', os.path.join(basedir, "app", "static"))
    TEMPLATE_FOLDER = os.environ.get('TEMPLATE_FOLDER', os.path.join(basedir, "app", "templates"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_app(cls, app):
        if not os.path.exists(cls.STATIC_FOLDER):
            os.makedirs(cls.STATIC_FOLDER)
        if not os.path.exists(cls.TEMPLATE_FOLDER):
            os.makedirs(cls.TEMPLATE_FOLDER)


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, 'data_dev.sqlite')}"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, 'data_test.sqlite')}"
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, 'data.sqlite')}"
    )


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
}
