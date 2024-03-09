from datetime import datetime
from flask import Flask, render_template, request, url_for, send_file
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
    return render_template("list.htm", tasks=tasks(name, action=False), list=name)


@app.post("/tasks/<list>")
def tasks(list: str, *, action=True):
    if action:
        Task.create(
            request.form["desc"],
            list,
            (
                datetime.strptime(request.form["duefor"], "%Y-%m-%d")
                if request.form["duefor"]
                else None
            ),
        )
    with Session() as session:
        return render_template(
            "tasks.htm",
            list=list,
            tasks=session.query(Task).filter_by(list=list).all(),
            fact=random_fact(),
        )


@app.post("/update/<list>")
def updatetasks(list: str):
    donetasks = [int(taskid) for taskid in request.form]
    with Session() as session:
        for task in session.query(Task).filter_by(list=list).all():
            if task.done and task.id not in donetasks:
                Task.update(list, task.id, newdone=False)
            if not task.done and task.id in donetasks:
                Task.update(list, task.id, newdone=True)
    return tasks(list, action=False)


# misc
@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
