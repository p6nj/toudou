from datetime import date
from flask import Blueprint, redirect, url_for
from flask_httpauth import HTTPTokenAuth
from toudou.config import config
from toudou.models import (
    List,
    ListNotFoundError,
    Task,
    ListExistsError,
    TaskExistsError,
    TaskNotFoundError,
)
from spectree import SecurityScheme, SpecTree
from pydantic.v1 import BaseModel, conlist, constr, condate, conint

spec = SpecTree(
    "flask",
    security_schemes=[
        SecurityScheme(name="bearer_token", data={"type": "http", "scheme": "bearer"})
    ],
    security=[{"bearer_token": []}],
)
auth = HTTPTokenAuth(scheme="Bearer")

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
    static_url_path="../static",
    template_folder="../templates",
)

tokens = {
    config["API_USER1_TOKEN"]: config["API_USER1"],
    config["API_USER2_TOKEN"]: config["API_USER2"],
}


@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]


# doing it the Python way
def real(o, check=False):
    if check:
        o.__getreal__(checklist=check)
    return o.__getreal__()


class ConstrainedTask(BaseModel):
    desc: constr(max_length=255)  # type: ignore
    duefor: condate(gt=date(1980, 1, 1), lt=date(3000, 1, 1))  # type: ignore
    list: constr(max_length=255)  # type: ignore
    id: conint(lt=255) = None  # type: ignore
    done: bool = False

    def __getreal__(self, checklist=False) -> Task:
        if checklist and not List.exists(self.list):
            raise ListNotFoundError("can't create Task object: list not found")
        return Task(self.desc, self.duefor, self.list, id=self.id, done=self.done)


class ConstrainedList(BaseModel, List):
    name: constr(max_length=255)  # type: ignore
    items: conlist(ConstrainedTask, max_items=255, unique_items=1)  # type: ignore

    def __getreal__(self) -> List:
        return List(self.name, [real(task) for task in self.items])


class Lists(BaseModel):
    inner: conlist(ConstrainedList, max_items=255, unique_items=1)  # type: ignore

    def __getreal__(self) -> list[List]:
        return [real(list) for list in self.inner]


class Tasks(BaseModel):
    inner: conlist(ConstrainedTask, max_items=255, unique_items=1)  # type: ignore

    def __getreal__(self) -> list[Task]:
        return [real(task) for task in self.inner]


# lists
@api.post("/lists")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def createlists(lists: Lists):
    try:
        for list in real(lists):
            list.create()
    except ListExistsError as e:
        return f"List `{e}` already exists", 400
    return redirect(url_for("lists"))


@api.post("/list")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def createlist(list: ConstrainedList):
    try:
        real(list).create()
    except ListExistsError:
        return "List already exists", 400
    return redirect(url_for("list/" + real(list).name))


@api.get("/lists")
@spec.validate(tags=["api", "lists"])
def readlists():
    return {list.name: dict(list) for list in List.all()}


@api.get("/list/<name>")
@spec.validate(tags=["api", "lists"])
def readlist(name: str):
    try:
        return dict(List.read(name))
    except ListNotFoundError:
        return "List not found", 400


@api.patch("/lists")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def updatelists(lists: Lists):
    delalllists()
    return createlists(lists)


@api.patch("/list/<name>")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def updatelist(name: str, list: ConstrainedList):
    List.read(name).delete()
    return createlist(list)


@api.delete("/lists")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def delalllists():
    for list in List.all():
        list.delete()
    return redirect(url_for("lists"))


@api.delete("/list/<name>")
@auth.login_required
@spec.validate(tags=["api", "lists"])
def dellist(name: str):
    try:
        List.read(name).delete()
    except ListNotFoundError:
        return "List not found", 400
    return redirect(url_for("lists"))


# tasks
@api.post("/tasks")
@auth.login_required
@spec.validate(tags=["api", "tasks"])
def createtasks(tasks: Tasks):
    try:
        for task in real(tasks):
            task.create()
    except TaskExistsError as e:
        return f"Task {e} already exists", 400
    return redirect(url_for("tasks"))


@api.post("/task")
@auth.login_required
@spec.validate(tags=["api", "tasks"])
def createtask(task: ConstrainedTask):
    try:
        real(task).create()
    except TaskExistsError:
        return "Task already exists", 400
    return redirect(url_for("list/" + real(task).list + "/" + real(task).id))


@api.get("/tasks")
@spec.validate(tags=["api", "tasks"])
def readtasks():
    return readlists()


@api.get("/list/<list>/<id>")
@spec.validate(tags=["api", "tasks"])
def readtask(list: str, id: int):
    try:
        return dict(Task.read(id, list))
    except TaskNotFoundError:
        return "Task not found", 400


@api.patch("/tasks")
@auth.login_required
@spec.validate(tags=["api", "tasks"])
def updatetasks(tasks: Tasks):
    delalltasks()
    return createtasks(tasks)


@api.patch("/list/<list>/<id>")
@auth.login_required
@spec.validate(tags=["api", "tasks"])
def updatetask(list: str, id: int, task: ConstrainedTask):
    Task.read(id, list).delete()
    return createtask(task)


@api.delete("/tasks")
@auth.login_required
@spec.validate(tags=["api", "tasks"])
def delalltasks():
    for task in Task.all():
        task.delete()
    return redirect(url_for("tasks"))


@api.delete("/list/<list>/<id>")
@spec.validate(tags=["api", "tasks"])
def deltask(list: str, id: int):
    try:
        Task.read(id, list).delete()
    except TaskNotFoundError:
        return "Task not found", 400
    return redirect(url_for("tasks"))
