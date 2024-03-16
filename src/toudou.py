from os import path
from flask import Flask, send_from_directory
from views.cli import cli


def create_app():
    app = Flask(__name__)
    from views.web import web_ui

    app.register_blueprint(web_ui)

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    return app
