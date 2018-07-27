Hello Bene (and anyone else who might review this),

Just a quick introduction to the code..

The work_tracker application is an API that is intended to be the backend for a
ReactJs application (which is very bare bones at the moments).

There are a few areas for improvement, especially with error reporting ,and there are
a few '#todo's throughtout the project.

Let me know if you have any questions and I am interested to hear your critique.

Many thanks,
Robert

PROJECT STRUCTURE:

 - db.py
     - A factory that connects allows us to connect to a database.
       From each database class we can create a database table object that allows us
       interact with a database table with simple sql commands - INSERT, DELETE, UPSERT

 - work_tracker.py
     - Uses db.py to connect to the database and generates a database table object
       for each of the database tables in our applciation - WORK_TRACKER_LOG, TASKS and USERS.
       The work_tracker functions allows us to interact with the database in 5 ways:
         - Create user - Inserts a user in the USERS table
         - Get user_id - Returns the user_id for a given user
         - Create task - Inserts a task in the TASKs table
         - Get task_id - Returns the task_id for a given task
         - Log task - Logs a task, given a corect task_id/user_id

 - app.py
     - This is a simple flask application that allows us to interact with work tracker

 - analyse.py
     - A slight tangent that I got lost in to be able to analyse the time spent working.
       The intention is to be able to pass back restructured data as json to the React application
       which is then rendered in d3js to provide analytics on time spent working on different tasks.
       I don't know why I thought I could do this in three hours.
