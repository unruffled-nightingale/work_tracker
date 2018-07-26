create table tasks
  ( task_id serial
   , task varchar(100)
   , tstamp timestamp default now()
   , primary key (task_id)
   , unique (task)
   )