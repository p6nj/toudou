from datetime import datetime
from io import BytesIO
from os import linesep
from flask import Flask, render_template, request, url_for, send_file
from models import List, Session, Task
from py8fact import random_fact
from services.csv import export as exportcsv, _import as importcsv

app = Flask(__name__)


@app.route("/")
def index():
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
    print(donetasks)
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


@app.route("/dellist/<list>")
def dellist(list: str):
    List.delete(list)
    return nav()


@app.route("/deltask/<list>/<int:task>")
def deltask(list: str, task: int):
    Task.delete(list, task)
    return tasks(list, action=False)


@app.post("/modtask/<list>/<int:task>")
def modtask(list: str, task: int):
    Task.update(
        list,
        task,
        newdesc=request.form["desc"],
        newduefor=(
            datetime.strptime(request.form["duefor"], "%Y-%m-%d")
            if "yesdate" in request.form
            and "duefor" in request.form
            and request.form["duefor"]
            else False
        ),
    )
    return tasks(list, action=False)


@app.post("/modlist/<list>")
def modlist(list: str):
    print(request.form["name"])
    List.update(list, request.form["name"])
    return nav()


@app.route("/download")
def downloadcsv():
    buffer = BytesIO()
    buffer.write(exportcsv().encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer, as_attachment=True, download_name="toudou.csv", mimetype="text/csv"
    )


@app.post("/upload")
def upload():
    importcsv(
        linesep.join(request.files["file"].read().decode("utf-8").splitlines()[1:])
    )
    return render_template("okimport.htm")


# misc
@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# static files
with app.test_request_context():
    url_for("static", filename="custom.css")
