create table users
   ( user_id serial
   , user_name varchar(100)
   , tstamp timestamp default now()
   , primary key (user_id)
   , unique(user_name)
   )