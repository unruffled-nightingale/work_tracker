create table work_tracker_log
   ( user_id varchar(100)
   , task varchar(4000)
   , tstamp timestamp default now()
   )