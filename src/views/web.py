from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route("/")
def hello(name=None):
    return render_template("home.html", name=name)


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
