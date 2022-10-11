import os

from flask import render_template
from flask_script import Manager, Shell
from werkzeug import exceptions as werkzeug_exceptions

from app import create_app, db

curr_app = create_app(os.environ.get('FLASK_CONFIG', 'dev'))
manager = Manager(curr_app)


@curr_app.errorhandler(werkzeug_exceptions.BadRequest)
def handle_bad_request(e):
    return render_template('errors/400.html'), 400


@curr_app.errorhandler(werkzeug_exceptions.Unauthorized)
def handle_unauthorized(e):
    return render_template('errors/401.html'), 401


@curr_app.errorhandler(werkzeug_exceptions.NotFound)
def handle_not_found(e):
    return render_template('errors/404.html'), 404


@curr_app.errorhandler(werkzeug_exceptions.InternalServerError)
def handle_internal_server_error(e):
    return render_template('errors/500.html'), 500


def make_shell_context():
    return dict(app=curr_app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def init_db():
    db.create_all()


if __name__ == "__main__":
    manager.run()
