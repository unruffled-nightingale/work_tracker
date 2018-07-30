from db import DatabaseFactory
from psycopg2 import IntegrityError
from analyse import Analyse

# todo Move to proper ORM - just making more work for myself


class WorkTracker(object):

    def __init__(self, db_connection):

        self.db = DatabaseFactory.connect('Postgres', db_connection)

        self.db.connect()

        # Instantiate database table object
        self.work_tracker_log = self.db.get_table(db_connection['user'], 'work_tracker_log')
        self.current_tasks = self.db.get_table(db_connection['user'], 'current_tasks')
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
        :param data:  Dictionary, schema: {'user' : ${user}}
        """
        result = self.users.select(data)
        if result:
            return result[0]['user_id']
        return {}

    def add_current_task(self, data):
        """
        Inserts a task into the table current_tasks
        :param data: Dictionary, schema: {'user_id' : ${user_id}, 'task_id': ${task_id}}
        """
        try:
            self.current_tasks.insert(data)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
        except Exception:
            self.db.rollback()
            raise InsertError('Insert failed')

    def delete_current_task(self, data):
        """
        Deletes a task into the table current_tasks
        :param data: Dictionary, schema: {'user_id' : ${user_id}, 'task_id': ${task_id}}
        """
        try:
            self.current_tasks.delete(data)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise InsertError('Delete failed')

    def get_current_tasks(self, data):
        """
        Returns all current_tasts from the table current_tasks for a particular user
        :param data: Dictionary, schema: {'user_id' : ${user_id}}
        """
        sql = """
           select t.task_id, t.task
             from %s c
             join %s t
               on c.task_id = t.task_id
            where c.user_id = %s
        """ % (self.current_tasks._name, self.tasks._name, '%(user_id)s')
        self.db._cur.execute(sql, data)
        cols = [desc[0] for desc in self.db._cur.description]
        data = self.db._cur.fetchall()
        self.db.commit()
        return [dict(zip(cols, row)) for row in data]

    def get_bar_graph_data(self, data):
        """
        Returns the bar graph data for a particular user
        :param data: Dictionary, schema: {'user_id' : ${user_id}}
        """
        sql = """
           select l.user_id, t.task, l.tstamp
             from %s l
             join %s t
               on l.task_id = t.task_id
            where l.user_id = %s
            order by l.tstamp asc
        """ % (self.work_tracker_log._name, self.tasks._name, '%(user_id)s')
        self.db._cur.execute(sql, data)
        cols = [desc[0] for desc in self.db._cur.description]
        data = self.db._cur.fetchall()
        self.db.commit()
        log_data = [dict(zip(cols, row)) for row in data]
        return Analyse(log_data).get_bar_grouping_json()


class InsertError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))
