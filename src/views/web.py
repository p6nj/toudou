from datetime import datetime
from flask import Flask, render_template, request, url_for, send_file
from models import List, Session, Task
from py8fact import random_fact

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html", nav=nav(), main=home())


@app.route("/nav")
def nav(*, newlist=False):
    with Session() as session:
        return render_template(
            "nav.htm",
            lists=[list.name for list in session.query(List).all()],
            newlist=newlist,
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


@app.route("/newlist", methods=["POST", "GET"])
def newlist():
    if request.method == "GET":
        return render_template("newlist.htm")
    else:
        List.create(request.form["name"])
        return nav(newlist=True)


# misc
@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
