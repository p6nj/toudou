from flask import Flask, render_template, url_for
from models import List, Session

app = Flask(__name__)


@app.route("/")
def hello():
    with Session() as session:
        return render_template(
            "home.html", lists=[list.name for list in session.query(List).all()]
        )


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
