from flask import Flask, render_template, url_for, send_file
from models import List, Session

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("home.html", nav=nav())


@app.route("/nav")
def nav():
    with Session() as session:
        return render_template(
            "nav.htm", lists=[list.name for list in session.query(List).all()]
        )


@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
