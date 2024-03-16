from os import path
from flask import Flask, render_template, send_from_directory
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

    @app.errorhandler(500)
    def handle_internal_error(error):
        return render_template("error.htm")

    return app
