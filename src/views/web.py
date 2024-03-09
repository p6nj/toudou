from flask import Flask, render_template, url_for, send_file
from models import List, Session

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html", header=header(), main=home())


@app.route("/header/<int:new>/<current>")
def header(*, new: bool = False, current: str = None):
    with Session() as session:
        return render_template(
            "header.htm",
            lists=[list.name for list in session.query(List).all()],
            new=new,
            current=current,
        )


# main fillers
@app.route("/home")
def home():
    return render_template("home.htm")


# misc
@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
