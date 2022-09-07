import argparse
import os

from app import create_app, db

application = create_app(os.environ.get('FLASK_CONFIG', 'dev'))
db.create_all(app=application)

# @application.errorhandler(werkzeug_exceptions.BadRequest)
# def handle_bad_request(e):
#     return render_template('errors/400.html'), 400
#
#
# @application.errorhandler(werkzeug_exceptions.Unauthorized)
# def handle_unauthorized(e):
#     return render_template('errors/401.html'), 401
#
#
# @application.errorhandler(werkzeug_exceptions.NotFound)
# def handle_not_found(e):
#     return render_template('errors/404.html'), 404
#
#
# @application.errorhandler(werkzeug_exceptions.InternalServerError)
# def handle_internal_server_error(e):
#     return render_template('errors/500.html'), 500

# @application.before_first_request
# def create_db():
#     db.create_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=False, default="127.0.0.1", type=str)
    parser.add_argument("--port", required=False, default=5000, type=int)
    args = parser.parse_args()

    application.run(host=args.host, port=args.port)
