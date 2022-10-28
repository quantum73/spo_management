import logging

from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import config

csrf = CSRFProtect()
cors = CORS(origins=["localhost", "127.0.0.1", "0.0.0.0"])
bootstrap = Bootstrap4()
db = SQLAlchemy()


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt='%(asctime)s | <%(name)s> | [%(levelname)s] | %(message)s',
        datefmt='%H:%M:%S %d.%m.%Y',
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    csrf.init_app(app)
    cors.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
