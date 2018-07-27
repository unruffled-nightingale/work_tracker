import unittest
from work_tracker import WorkTracker, InsertError
import psycopg2

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

        # Instantiate our WorkTracker class that we will be testing
        cls.wk = WorkTracker(DEV_PG_CONNECION)

    @classmethod
    def tearDownClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()

        # Drop test tables
        sql = "drop table work_tracker_log"
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
