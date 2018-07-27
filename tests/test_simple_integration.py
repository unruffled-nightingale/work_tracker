import unittest
import psycopg2
import requests
import json

from GLOBALS import DEV_PG_CONNECION, API_ROOT

class TestSimpleIntegration(unittest.TestCase):

    """
    Simple integration test that checks the functionality of the API.
    Requires the API to be running and the database objects exist
    """

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()


    @classmethod
    def tearDownClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()

        # Drop test tables
        sql = "delete from work_tracker_log"
        cls.cur.execute(sql)

        sql = "delete from tasks"
        cls.cur.execute(sql)

        # Create table to test
        sql = "delete from users"
        cls.cur.execute(sql)
        cls.conn.commit()

    def test_integration(self):

        # Create two users
        msg = {'user_name': 'test user'}
        response = requests.post('http://localhost:5000/add_user', json=msg)
        user_id = json.loads(response.text)['user_id']

        msg = {'user_name': 'test user'}
        requests.post('http://localhost:5000/add_user', json=msg)

        msg = {'user_name': 'test user2'}
        response = requests.post('http://localhost:5000/add_user', json=msg)

        # Create two tasks
        msg = {'task': 'test task1'}
        response = requests.post('http://localhost:5000/add_task', json=msg)
        task_id = json.loads(response.text)['task_id']

        msg = {'task': 'test task2'}
        requests.post('http://localhost:5000/add_task', json=msg)

        # Log a task
        msg = {'task_id': task_id, 'user_id': user_id}
        requests.post('http://localhost:5000/log_task', json=msg)

        self.cur.execute('select count(*) from users')
        result = self.cur.fetchall()[0][0]
        self.assertEqual(result, 2)

        self.cur.execute('select count(*) from tasks')
        result = self.cur.fetchall()[0][0]
        self.assertEqual(result, 2)

        self.cur.execute('select user_id, task_id from work_tracker_log')
        result = self.cur.fetchall()
        self.assertEqual(result, [(user_id, task_id)])
