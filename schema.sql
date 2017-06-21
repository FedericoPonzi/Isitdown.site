CREATE TABLE IF NOT EXISTS pings (id serial primary key, f varchar not null, t varchar not null, at timestamp not null, down boolean not null);
