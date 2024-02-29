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