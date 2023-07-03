CREATE SCHEMA IF NOT EXISTS auth;

create table "user" (
    id uuid not null constraint auth_user_pkey primary key,
    password varchar(128) not null,
    is_superuser boolean not null,
    first_name varchar(150) not null,
    last_name varchar(150) not null,
    email varchar(254) not null,
    created_at timestamp with time zone not null,
    updated_at timestamp with time zone not null
);
alter table "user"
    owner to user1;

create unique index user_email_uindex
    on "user" (email);

create table role
(
    id          uuid         not null
        constraint role_pk
            primary key,
    name        varchar(150) not null,
    description text
);

alter table role
    owner to user1;

create unique index role_name_uindex
    on role (name);

create unique index role_table_key
    on role (name);

create table user_role
(
    id         uuid      not null
        constraint user_role_pk
            primary key,
    user_id    uuid
        constraint user_id__fk
            references "user"
            on delete cascade,
    role_id    uuid
        constraint role_id___fk
            references role
            on delete cascade,
    created_at timestamp not null
);

alter table user_role
    owner to user1;

create unique index user_role_user_id_role_id_uindex
    on user_role (user_id, role_id);

create table device
(
    id         uuid not null
        constraint device_pk
            primary key,
    user_agent text not null
);

alter table device
    owner to user1;

create unique index device_user_agent_uindex
    on device (user_agent);

create table user_remember_device
(
    id        uuid not null
        constraint user_remember_device_pk
            primary key,
    device_id uuid not null
        constraint device_id___fk
            references device
            on delete cascade,
    user_id   uuid not null
        constraint user_id___fk
            references "user"
            on delete cascade
);

alter table user_remember_device
    owner to user1;

create unique index device_user__index
    on user_remember_device (user_id, device_id);

create table action_type
(
    id   uuid not null
        constraint action_type_pk
            primary key,
    name varchar(150)
);

alter table action_type
    owner to user1;

create table history
(
    id         uuid        not null
        constraint history_pk
            primary key,
    user_id    uuid        not null
        constraint user_id___fk
            references "user",
    action_id  uuid        not null
        constraint action_id___fk
            references action_type
            on delete cascade,
    ipv4       varchar(15) not null,
    device_id  uuid        not null
        constraint device_id___fk
            references device
            on delete cascade,
    created_at timestamp   not null
);

alter table history
    owner to user1;

create unique index action_type_name_uindex
    on action_type (name);

