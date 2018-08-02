import unittest
from work_tracker import WorkTracker, InsertError
import psycopg2
import time
import json

from GLOBALS import DEV_PG_CONNECION


class TestPostgresTable(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()

        # Create test tables
        sql = """
           create table users
               ( user_id serial
               , user_name varchar(100)
               , tstamp timestamp default now()
               , primary key (user_id)
               , unique(user_name)
               )
        """
        cls.cur.execute(sql)

        sql = """
           create table tasks
              ( task_id serial
               , task varchar(100)
               , tstamp timestamp default now()
               , primary key (task_id)
               , unique (task)
               )
        """
        cls.cur.execute(sql)

        sql = """
            create table work_tracker_log
               ( user_id integer references users(user_id)
               , task_id integer references tasks(task_id)
               , tstamp timestamp default now()
               )
        """
        cls.cur.execute(sql)
        cls.conn.commit()

        sql = """
            create table current_tasks
               ( user_id integer references users(user_id)
               , task_id integer references tasks(task_id)
               , tstamp timestamp default now()
               , primary key (user_id, task_id)
               )
            """
        cls.cur.execute(sql)
        cls.conn.commit()

        # Instantiate our WorkTracker class that we will be testing
        cls.wk = WorkTracker(DEV_PG_CONNECION)

    @classmethod
    def tearDownClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()
        cls.conn.commit()

        # Drop test tables
        sql = "drop table work_tracker_log"
        cls.cur.execute(sql)

        # Drop test tables
        sql = "drop table current_tasks"
        cls.cur.execute(sql)

        sql = "drop table tasks"
        cls.cur.execute(sql)

        # Create table to test
        sql = "drop table users"
        cls.cur.execute(sql)
        cls.conn.commit()

    def tearDown(self):
        self.conn.rollback()
        sql = "delete from work_tracker_log"
        self.cur.execute(sql)
        sql = "delete from current_tasks"
        self.cur.execute(sql)
        sql = "delete from tasks"
        self.cur.execute(sql)
        sql = "delete from users"
        self.cur.execute(sql)
        self.conn.commit()

    def test_add_task(self):
        """ Testing that we can insert into tasks """
        self.wk.add_task({'task': 'test'})
        self.cur.execute('select task from tasks')
        result = self.cur.fetchall()
        expected = [('test', )]
        self.assertEqual(expected, result)

    def test_add_task_dupe(self):
        """ Testing that we do not error on primary key violation """
        self.cur.execute("insert into tasks (task) values ('test')")
        self.conn.commit()
        self.wk.add_task({'task': 'test'})
        self.cur.execute('select task from tasks')
        result = self.cur.fetchall()
        expected = [('test',)]
        self.assertEqual(expected, result)

    def test_add_task_insert_error(self):
        """ Testing that we error on bad insert """
        with self.assertRaises(InsertError):
            self.wk.add_task({'unknown': 'bad value'})

    def test_get_task_id(self):
        """ Testing that we error on bad insert """
        self.cur.execute("insert into tasks (task) values ('test')")
        self.conn.commit()
        result = self.wk.get_task_id({'task': 'test'})
        self.cur.execute('select task_id from tasks')
        task_id = self.cur.fetchall()[0][0]

        self.assertEqual(result, task_id)

    def test_get_task_id_null(self):
        """ Testing that we error on bad insert """
        result = self.wk.get_task_id({'task': 'test'})
        expected = {}
        self.assertEqual(result, expected)

    def test_add_user(self):
        """ Testing that we can insert into users """
        self.wk.add_user({'user_name': 'test user'})
        self.cur.execute('select user_name from users')
        result = self.cur.fetchall()
        expected = [('test user',)]
        self.assertEqual(expected, result)

    def test_add_user_dupe(self):
        """ Testing that we do not error on primary key violation """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.conn.commit()
        self.wk.add_user({'user_name': 'test user'})
        self.cur.execute('select user_name from users')
        result = self.cur.fetchall()
        expected = [('test user',)]
        self.assertEqual(expected, result)

    def test_add_user_insert_error(self):
        """ Testing that we error on bad insert """
        with self.assertRaises(InsertError):
            self.wk.add_user({'unknown': 'bad value'})

    def test_get_user_id(self):
        """ Testing that we error on bad insert """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.conn.commit()
        result = self.wk.get_user_id({'user_name': 'test user'})
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.assertEqual(result, user_id)

    def test_get_user_id_null(self):
        """ Testing that we error on bad insert """
        result = self.wk.get_task_id({'user': 'test user'})
        expected = {}
        self.assertEqual(result, expected)

    def test_log_task(self):
        """ Testing that we can insert into users """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test')")
        self.cur.execute('select task_id from tasks')
        self.conn.commit()
        task_id = self.cur.fetchall()[0][0]
        self.wk.log_task({'user_id': user_id, 'task_id': task_id})
        self.cur.execute('select task_id, user_id from work_tracker_log')
        result = self.cur.fetchall()
        expected = [(task_id, user_id)]
        self.assertEqual(result, expected)

    def test_log_task_error_no_reference(self):
        """ Testing that we can insert into users """
        with self.assertRaises(InsertError):
            self.wk.log_task({'user_id': 1, 'task_id': 1})

    def test_add_current_task(self):
        """ Testing that we can insert into users """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test')")
        self.cur.execute('select task_id from tasks')
        self.conn.commit()
        task_id = self.cur.fetchall()[0][0]
        self.wk.add_current_task({'user_id': user_id, 'task_id': task_id})
        self.cur.execute('select task_id, user_id from current_tasks')
        result = self.cur.fetchall()
        expected = [(task_id, user_id)]
        self.assertEqual(result, expected)

    def test_add_current_task_dupe(self):
        """ Testing that we can insert into users """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test')")
        self.cur.execute('select task_id from tasks')
        self.conn.commit()
        task_id = self.cur.fetchall()[0][0]
        self.wk.add_current_task({'user_id': user_id, 'task_id': task_id})
        self.wk.add_current_task({'user_id': user_id, 'task_id': task_id})
        self.cur.execute('select task_id, user_id from current_tasks')
        result = self.cur.fetchall()
        expected = [(task_id, user_id)]
        self.assertEqual(result, expected)

    def test_add_current_task_insert_error(self):
        """ Testing that we error on bad insert """
        with self.assertRaises(InsertError):
            self.wk.add_current_task({'unknown': 'bad value'})

    def test_delete_current_task(self):
        """ Testing that we can delete from current_tasks"""
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test')")
        self.cur.execute('select task_id from tasks')
        task_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into current_tasks (user_id, task_id) values (%s, %s)", (user_id, task_id))
        self.conn.commit()
        self.wk.delete_current_task({'user_id': user_id, 'task_id': task_id})
        self.cur.execute('select count(*) from current_tasks')
        result = self.cur.fetchall()[0][0]
        self.assertEqual(result, 0)

    def test_delete_current_task_no_records(self):
        """ Testing that we do not error when deleting from current_tasks if the records does not exist"""
        self.wk.delete_current_task({'user_id': 999, 'task_id': 999})

    def test_get_current_tasks(self):
        """ Testing that we can delete from current_tasks"""
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test 1')")
        self.cur.execute("insert into tasks (task) values ('test 2')")
        self.cur.execute('select task_id from tasks')
        task_ids = self.cur.fetchall()
        task_id_1 = task_ids[0][0]
        task_id_2 = task_ids[1][0]
        self.cur.execute("insert into current_tasks (user_id, task_id) values (%s, %s)", (user_id, task_id_1))
        self.cur.execute("insert into current_tasks (user_id, task_id) values (%s, %s)", (user_id, task_id_2))
        self.conn.commit()
        result = self.wk.get_current_tasks({'user_id': user_id})
        expected = [{'task': 'test 1', 'task_id': 1}, {'task': 'test 2', 'task_id': 2}]
        self.assertEqual(result, expected)

    def test_get_current_tasks_no_records(self):
        """ Testing that we can delete from current_tasks"""
        result = self.wk.get_current_tasks({'user_id': 999})
        self.assertEqual(result, [])

    def test_get_bar_data(self):
        """
        Returns the bar graph data for a particular user
        :param data: Dictionary, schema: {'user_id' : ${user_id}}
        """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test 1')")
        self.cur.execute('select task_id from tasks')
        self.cur.execute("insert into tasks (task) values ('test 2')")
        self.cur.execute('select task_id from tasks')
        task_ids = self.cur.fetchall()
        task_id_1 = task_ids[0][0]
        task_id_2 = task_ids[1][0]
        data = {'user_id': user_id, 'task_id': task_id_1}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        time.sleep(2)
        data = {'user_id': user_id, 'task_id': task_id_2}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        time.sleep(2)
        data = {'user_id': user_id, 'task_id': task_id_1}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        data = {'user_id': user_id}
        result = self.wk.get_bar_graph_data(data)
        expected = [{"x":"test 1","y":2},{"x":"test 2","y":2}]
        self.assertEqual(expected, result)

    def test_get_line_data(self):
        """
        Returns the line graph data for a particular user
        :param data: Dictionary, schema: {'user_id' : ${user_id}}
        """
        self.cur.execute("insert into users (user_name) values ('test user')")
        self.cur.execute('select user_id from users')
        user_id = self.cur.fetchall()[0][0]
        self.cur.execute("insert into tasks (task) values ('test 1')")
        self.cur.execute('select task_id from tasks')
        self.cur.execute("insert into tasks (task) values ('test 2')")
        self.cur.execute('select task_id from tasks')
        task_ids = self.cur.fetchall()
        task_id_1 = task_ids[0][0]
        task_id_2 = task_ids[1][0]
        data = {'user_id': user_id, 'task_id': task_id_1}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        time.sleep(2)
        data = {'user_id': user_id, 'task_id': task_id_2}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        time.sleep(2)
        data = {'user_id': user_id, 'task_id': task_id_1}
        self.cur.execute("insert into work_tracker_log (user_id, task_id) values (%(user_id)s, %(task_id)s)", data)
        self.conn.commit()
        data = {'user_id': user_id}
        result = self.wk.get_line_graph_data(data)
        expected = [
            [
                {'x': '2018-08-02 19:22:23.998827', 'y': 0},
                {'x': '2018-08-02 19:22:26.086720', 'y': 2}
            ], [
                {'x': '2018-08-02 19:22:26.086720', 'y': 0},
                {'x': '2018-08-02 19:22:28.111687', 'y': 2}]
        ]
        # todo pass in tstamp so we can predict result

