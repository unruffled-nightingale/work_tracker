create table work_tracker_log
   ( user_id integer references users(user_id)
   , task_id integer references tasks(task_id)
   , tstamp timestamp default now()
   );