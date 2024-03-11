from flask import Flask
from views.cli import cli


def create_app():
    app = Flask(__name__)
    from views.web import web_ui

    app.register_blueprint(web_ui)
    return app
