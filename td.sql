create table if not exists list (
    name text not null primary key
);

create table if not exists task (
    id integer,
    desc text not null,
    done boolean default false,
    duefor date,
    list text not null,
    primary key (list, id),
    foreign key (list) references list (name) on delete cascade
);

CREATE TABLE if not exists taskcount (
    list TEXT PRIMARY KEY,
    n INTEGER DEFAULT 0,
    foreign key (list) references list (name) on delete cascade
);

CREATE TRIGGER if not exists increment
AFTER INSERT ON task
FOR EACH ROW
BEGIN
    update task
    set id = (
        select n from taskcount where list = new.list
    )
    where list = new.list and id is null;
    UPDATE taskcount
    SET n = n + 1
    WHERE list = NEW.list;
END;

CREATE TRIGGER if not exists decrement
AFTER DELETE ON task
FOR EACH ROW
BEGIN
    UPDATE taskcount
    SET n = n - 1
    WHERE list = OLD.list;
END;

create trigger if not exists newlist
after insert on list
for each ROW
BEGIN
    insert into taskcount(list) values (new.name);
END;