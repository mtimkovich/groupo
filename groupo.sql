create table users (
    id serial primary key,
    facebook_id integer unique not null,
    first_name varchar(35) not null,
    last_name varchar(35) not null,
    created timestamp not null
)
