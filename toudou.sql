create table if not exists list (
    name text not null primary key
);

create table if not exists task (
    id integer not null primary key autoincrement,
    desc text not null,
    done boolean default false,
    duefor date,
    list text not null,
    foreign key (list) references list (name)
);