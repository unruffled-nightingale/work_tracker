from db import DatabaseFactory
from psycopg2 import IntegrityError

# todo Improve exception handling
# todo Remove dependency on psycopg2

class WorkTracker(object):

    def __init__(self, db_connection):

        self.db = DatabaseFactory.connect('Postgres', db_connection)

        self.db.connect()

        # Instantiate database table object
        self.work_tracker_log = self.db.get_table(db_connection['user'], 'work_tracker_log')
        self.tasks = self.db.get_table(db_connection['user'], 'tasks')
        self.users = self.db.get_table(db_connection['user'], 'users')

    def log_task(self, data):
        """
        Logs a task into the table work_tracker_log
        :param data: A python dictionary of the form {'task_id' : ${task_id}, 'user': ${user_id}}
        """
        try:
            self.work_tracker_log.insert(data)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise InsertError('The reference task/user cannot be found in the parent table')
        except Exception:
            self.db.rollback()
            raise InsertError('Insert failed')

    def add_task(self, data):
        """
        Inserts a task into the table tasks
        :param data: A python dictionary of the form {'task' : ${task}}
        """
        try:
            self.tasks.insert(data)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

        except Exception:
            self.db.rollback()
            raise InsertError('Insert Failed')

    def get_task_id(self, data):
        """
        Returns a task_id from table tasks
        :param data: A python dictionary of the form {'task' : ${task}}
        """
        result = self.tasks.select(data)
        if result:
            return result[0]['task_id']
        return {}

    def add_user(self, data):
        """
        Inserts a user into the table users
        :param data: A python dictionary of the form {'user' : ${user}}
        """
        try:
            self.users.insert(data)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
        except Exception:
            self.db.rollback()
            raise InsertError('Insert Failed')

    def get_user_id(self, data):
        """
        Returns a user_id from table users
        :param data: A python dictionary of the form {'user' : ${user}}
        """
        result = self.users.select(data)
        if result:
            return result[0]['user_id']
        return {}


class InsertError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))