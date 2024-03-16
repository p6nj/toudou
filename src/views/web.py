from datetime import date
from io import BytesIO
from os import linesep
import traceback
from flask import render_template, request, send_file, Blueprint
from models import List, ListExistsError, Session, Task
from py8fact import random_fact
from services.csv import export as exportcsv, _import as importcsv
from .forms import (
    Task as TaskForm,
    List as ListForm,
    TaskMod as TaskModificationForm,
    ListMod as ListModificationForm,
)
from common import config

web_ui = Blueprint(
    "web_ui",
    __name__,
    url_prefix="/",
    static_url_path="static",
    template_folder="templates",
)


@web_ui.route("/")
def index():
    return render_template("index.html", nav=nav(), main=home())


@web_ui.route("/nav")
def nav(*, newlist=False):
    with Session() as session:
        return render_template(
            "nav.htm",
            lists=[list.name for list in session.query(List).all()],
            newlist=newlist,
        )


# main fillers
@web_ui.route("/home")
def home():
    return render_template("home.htm")


@web_ui.route("/list/<name>")
def list(name: str):
    return render_template(
        "list.htm",
        tasks=tasks(name, action=False),
        list=name,
        form=TaskForm(),
        renameform=ListModificationForm(),
    )


@web_ui.post("/tasks/<list>")
def tasks(list: str, *, action=True):
    if action:
        form = TaskForm()
        if form.validate_on_submit():
            Task.create(
                form.desc.data,
                list,
                form.duefor.data,
            )
    with Session() as session:
        return render_template(
            "tasks.htm",
            list=list,
            tasks=session.query(Task).filter_by(list=list).all(),
            fact=random_fact(),
            form=TaskModificationForm(),
        )


# this post request can't get its own FlaskForm :
# it contains a variable amount of ticket IDs
@web_ui.post("/update/<list>")
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


@web_ui.route("/newlist", methods=["POST", "GET"])
def newlist():
    if request.method == "GET":
        return render_template("newlist.htm", form=ListForm())
    else:
        form = ListForm()
        if form.validate_on_submit():
            try:
                List.create(form.name.data)
            except ListExistsError as e:
                if config["DEBUG"]:
                    traceback.print_exc()
        return nav(newlist=True)


@web_ui.route("/dellist/<list>")
def dellist(list: str):
    List.delete(list)
    return nav()


@web_ui.route("/deltask/<list>/<int:task>")
def deltask(list: str, task: int):
    Task.delete(list, task)
    return tasks(list, action=False)


@web_ui.post("/modtask/<list>/<int:task>")
def modtask(list: str, task: int):
    form = TaskModificationForm()
    if form.validate_on_submit():
        Task.update(
            list,
            task,
            newdesc=form.desc.data,
            newduefor=(form.yesdate.data and form.duefor.data),
        )
    return tasks(list, action=False)


@web_ui.post("/modlist/<list>")
def modlist(list: str):
    form = ListModificationForm()
    if form.validate_on_submit():
        List.update(list, form.name.data)
    return nav()


@web_ui.route("/download")
def downloadcsv():
    buffer = BytesIO()
    buffer.write(exportcsv().encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer, as_attachment=True, download_name="toudou.csv", mimetype="text/csv"
    )


# this function is executed when a file is chosen,
# no HTML form related error should be generated (no need for a custom list)
@web_ui.post("/upload")
def upload():
    importcsv(
        linesep.join(request.files["file"].read().decode("utf-8").splitlines()[1:])
    )
    return render_template("okimport.htm")
