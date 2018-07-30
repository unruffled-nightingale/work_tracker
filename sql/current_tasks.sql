create table current_tasks
   ( user_id integer references users(user_id)
   , task_id integer references tasks(task_id)
   , tstamp timestamp default now()
   , primary key (user_id, task_id)
   )