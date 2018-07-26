import unittest
from db import Postgres, PostgresTable, DatabaseFactory
import psycopg2

from GLOBALS import DEV_PG_CONNECION


class TestDatabaseFactory(unittest.TestCase):

    def test_connect_postgres(self):
        """Testing that we can connect to Poastgres through the factory"""
        DatabaseFactory.connect('Postgres', DEV_PG_CONNECION)

    def test_connect_bad_client(self):
        """Testing that we error if database does not exist"""
        with self.assertRaises(ImportError):
            DatabaseFactory.connect('Oracle', DEV_PG_CONNECION)


class TestPostgres(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Postgres(DEV_PG_CONNECION)


    def test_connect(self):
        """Testing that Postgres class can connect to database"""
        self.db.connect1()



class TestPostgresTable(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()

        # Create table to test
        sql = "create table ut_work_tracker (col_1 varchar(100), col_2 integer)"
        cls.cur.execute(sql)
        cls.conn.commit()

        # Instantiate our PostgresTable class
        schema = DEV_PG_CONNECION['user']
        name = 'ut_work_tracker'
        cls.table = PostgresTable(cls.cur, schema, name)


    @classmethod
    def tearDownClass(cls):
        cls.conn = psycopg2.connect(**DEV_PG_CONNECION)
        cls.cur = cls.conn.cursor()

        # Create table to test
        sql = "drop table ut_work_tracker"
        cls.cur.execute(sql)
        cls.conn.commit()

    def tearDown(self):
        sql = "delete from ut_work_tracker"
        self.cur.execute(sql)
        self.conn.commit()

    def test_insert(self):
        """Testing the insert function"""

        # Run insert function
        row = {'col_1': 'value_1', 'col_2': 2}
        self.table.insert(row)

        # Check the result
        self.cur.execute('select col_1, col_2 from ut_work_tracker')
        result = self.cur.fetchall()
        expected = [('value_1', 2)]
        self.assertEqual(set(result), set(expected))

    def test_insert_error(self):
        """Testing the error on the insert function"""
        pass

    def test_delete(self):
        """Testing the error on the insert function"""

        # Insert some values that we can delete
        sql = "insert into ut_work_tracker values ('value_1', 2)"
        self.cur.execute(sql)
        self.conn.commit()

        # Run insert function
        row = {'col_1': 'value_1', 'col_2': 2}
        self.table.delete(row)

        # Check that there are no records in the table
        self.cur.execute('select count(*) from ut_work_tracker')
        result = self.cur.fetchall()
        expected = [(0,)]
        self.assertEqual(result, expected)

    def test_delete_error(self):
        """Testing the error on the insert function"""
        pass


