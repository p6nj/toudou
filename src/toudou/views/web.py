from io import BytesIO
from os import linesep
import traceback
from flask import render_template, request, send_file, Blueprint
from toudou.models import List, ListExistsError, Task
from py8fact import random_fact
from toudou.services.csv import export as exportcsv, _import as importcsv
from .forms import (
    Task as TaskForm,
    List as ListForm,
    TaskMod as TaskModificationForm,
    ListMod as ListModificationForm,
)
from toudou.config import config

web_ui = Blueprint(
    "web_ui",
    __name__,
    url_prefix="/",
    static_url_path="../static",
    template_folder="../templates",
)


def create_app():
    from os import path
    from flask import Flask, render_template, send_from_directory

    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    app.config.from_prefixed_env()
    app.register_blueprint(web_ui)

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            path.join(app.root_path, "../static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        return render_template("error.htm")

    return app


@web_ui.route("/")
def index():
    return render_template("index.html", nav=nav(), main=home())


@web_ui.route("/nav")
def nav(*, newlist=False):
    return render_template(
        "nav.htm",
        lists=[list.name for list in List.all()],
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
            Task(form.desc.data, form.duefor.data, list).create()
    return render_template(
        "tasks.htm",
        list=list,
        tasks=Task.all(list=list),
        fact=random_fact(),
        form=TaskModificationForm(),
    )


# this post request can't get its own FlaskForm :
# it contains a variable amount of ticket IDs
@web_ui.post("/update/<list>")
def updatetasks(list: str):
    donetasks = [int(taskid) for taskid in request.form]
    print(donetasks)
    for task in Task.all(list=list):
        if task.done and task.id not in donetasks:
            Task.read(task.id, list).update(done=False)
        if not task.done and task.id in donetasks:
            Task.read(task.id, list).update(done=True)
    return tasks(list, action=False)


@web_ui.route("/newlist", methods=["POST", "GET"])
def newlist():
    if request.method == "GET":
        return render_template("newlist.htm", form=ListForm())
    else:
        form = ListForm()
        if form.validate_on_submit():
            try:
                List.empty(form.name.data).create()
            except ListExistsError as e:
                if config["DEBUG"]:
                    traceback.print_exc()
        return nav(newlist=True)


@web_ui.route("/dellist/<list>")
def dellist(list: str):
    List.read(list).delete()
    return nav()


@web_ui.route("/deltask/<list>/<int:task>")
def deltask(list: str, task: int):
    Task.read(task, list).delete()
    return tasks(list, action=False)


@web_ui.post("/modtask/<list>/<int:task>")
def modtask(list: str, task: int):
    form = TaskModificationForm()
    if form.validate_on_submit():
        Task.read(task, list).update(
            desc=form.desc.data,
            duefor=(form.yesdate.data and form.duefor.data),
        )
    return tasks(list, action=False)


@web_ui.post("/modlist/<list>")
def modlist(list: str):
    form = ListModificationForm()
    if form.validate_on_submit():
        List.read(
            list,
        ).update(form.name.data)
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
