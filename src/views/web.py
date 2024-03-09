from flask import Flask, render_template, url_for, send_file
from models import List, Session, Task
from py8fact import random_fact

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html", header=header(), main=home())


@app.route("/header")
def header():
    with Session() as session:
        return render_template(
            "header.htm", lists=[list.name for list in session.query(List).all()]
        )


# main fillers
@app.route("/home")
def home():
    return render_template("home.htm")


@app.route("/list/<name>")
def list(name: str):
    with Session() as session:
        return render_template(
            "list.htm",
            list=name,
            tasks=session.query(Task).filter_by(list=name).all(),
            fact=random_fact(),
        )


# misc
@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
