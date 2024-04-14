from datetime import date
from flask import Blueprint
from toudou.models import (
    List,
    ListNotFoundError,
    Task,
    ListExistsError,
    TaskExistsError,
    TaskNotFoundError,
)
from spectree import SpecTree
from pydantic.v1 import BaseModel, conlist, constr, condate, conint

spec = SpecTree("flask", annotations=True)

api = Blueprint(
    "api",
    __name__,
    url_prefix="/",
    static_url_path="../static",
    template_folder="../templates",
)


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
@spec.validate(tags=["api"])
def createlists(lists: Lists):
    try:
        for list in real(lists):
            list.create()
    except ListExistsError as e:
        return f"List `{e}` already exists", 400


@api.post("/list")
@spec.validate(tags=["api"])
def createlist(list: ConstrainedList):
    try:
        real(list).create()
    except ListExistsError:
        return "List already exists", 400


@api.get("/lists")
def readlists():
    return {list.name: dict(list) for list in List.all()}


@api.get("/list/<name>")
def readlist(name: str):
    try:
        return dict(List.read(name))
    except ListNotFoundError:
        return "List not found", 400


@api.patch("/lists")
@spec.validate(tags=["api"])
def updatelists(lists: Lists):
    delalllists()
    createlists(lists)


@api.patch("/list/<name>")
@spec.validate(tags=["api"])
def updatelist(name: str, list: ConstrainedList):
    List.read(name).delete()
    createlist(list)


@api.delete("/lists")
def delalllists():
    for list in List.all():
        list.delete()


@api.delete("/list/<name>")
def dellist(name: str):
    try:
        List.read(name).delete()
    except ListNotFoundError:
        return "List not found", 400


# tasks
@api.post("/tasks")
@spec.validate(tags=["api"])
def createtasks(tasks: Tasks):
    try:
        for task in real(tasks):
            task.create()
    except TaskExistsError as e:
        return f"Task {e} already exists", 400


@api.post("/task")
@spec.validate(tags=["api"])
def createtask(task: ConstrainedTask):
    try:
        real(task).create()
    except TaskExistsError:
        return "Task already exists", 400


@api.get("/tasks")
def readtasks():
    return {task.id: dict(task) for task in Task.all()}


@api.get("/list/<list>/<id>")
def readtask(list: str, id: int):
    try:
        return dict(Task.read(id, list))
    except TaskNotFoundError:
        return "Task not found", 400


@api.patch("/tasks")
@spec.validate(tags=["api"])
def updatetasks(tasks: Tasks):
    delalltasks()
    createtasks(tasks)


@api.patch("/list/<list>/<id>")
@spec.validate(tags=["api"])
def updatetask(list: str, id: int, task: ConstrainedTask):
    Task.read(id, list).delete()
    createtask(task)


@api.delete("/tasks")
def delalltasks():
    for task in Task.all():
        task.delete()


@api.delete("/list/<list>/<id>")
def deltask(list: str, id: int):
    try:
        Task.read(id, list).delete()
    except TaskNotFoundError:
        return "Task not found", 400
