-- Update db to work with the new schema. More readable and adds the response code column.
alter table pings rename column f to from_ip;
alter table pings rename column down to isdown;
alter table pings rename column t to host;
alter table pings rename column at to time_stamp;
alter table pings add column response_code int;
update pings set response_code = 200 where isdown = 'f';
