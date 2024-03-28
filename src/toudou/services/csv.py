from toudou.models import List, ListExistsError, Task, TaskExistsError
from os import linesep


# cute little function
def export():
    return linesep.join(
        [
            ",".join(("list", "task", "desc", "done", "date")),
            linesep.join(
                [
                    ",".join([list] + [str(entry) for entry in task])
                    for list in [list.name for list in List.all()]
                    for task in [
                        [
                            task.id,
                            task.desc,
                            int(task.done),
                            str(task.duefor) if task.duefor else "",
                        ]
                        for task in Task.all()
                    ]
                ]
            ),
        ]
    )


def _import(csv: str):
    """Import from CSV headless data."""
    from datetime import date as d

    lists = []
    for line in csv.splitlines():
        line = line.split(",")
        list = List.empty(line[0])
        task = int(line[1])
        desc = line[2]
        done = bool(int(line[3]))
        date = d.strptime(line[4], "%Y-%m-%d") if line[4] else None
        if list not in lists:
            try:
                list.create()
            except ListExistsError as e:
                print("list already exists: " + str(e))
            lists.append(list)
        task = Task(desc, date, list.name, id=task, done=done)
        try:
            task.create()
        except TaskExistsError as e:
            print("task already exists, replacing: " + str(e))
            task.delete()
            task.create()
