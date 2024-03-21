from .views import cli


def __import_config():
    global config
    from os import environ

    config = {
        k[7:]: True if v == "True" else False if v == "False" else v
        for k, v in environ.items()
        if k.startswith("TOUDOU_")
    }


def create_app():
    from os import path
    from flask import Flask, render_template, send_from_directory

    app = Flask(__name__)
    from toudou.views import web

    app.config.from_prefixed_env()
    app.register_blueprint(web)

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
