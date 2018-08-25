-- Update db after commit 
alter table pings rename column f to from_ip;
alter table pings rename column down to isdown;
alter table pings add column response int;
update pings set response = 200 where isdown = 'f';