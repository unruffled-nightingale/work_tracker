import unittest
from work_tracker import WorkTracker
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
        sql = "delete from work_tracker_log"
        self.cur.execute(sql)
        sql = "delete from tasks"
        self.cur.execute(sql)
        sql = "delete from users"
        self.cur.execute(sql)
        self.conn.commit()

    def test_add_task(self):
        self.wk.add_task({'task': 'test'})
        self.cur.execute('select task from tasks')
        result = self.cur.fetchall()
        expected = [('test', )]
        self.assertEqual(expected, result)

    def test_add_task_dupe(self):
        self.cur.execute("insert into tasks (task) values ('test')")
        self.wk.add_task({'task': 'test'})
        self.cur.execute('select task from tasks')
        result = self.cur.fetchall()
        expected = [('test', )]
        self.assertEqual(expected, result)