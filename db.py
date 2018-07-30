import psycopg2


class DatabaseFactory(object):

    # The list of available DB clients
    factories = ['Postgres']

    @staticmethod
    def connect(driver, connection):
        if driver in DatabaseFactory.factories:
            return eval(driver + '.Factory()').connect(connection)
        else:
            raise ImportError('Unknown client')


class Database(object):

    def __init__(self, connection):
        self._connection = connection
        self._cur = None
        self._conn = None

    def connect(self):
        pass

    def close(self):
        if self._conn:
            self._conn.close()

    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.commit()


class Postgres(Database):

    def connect(self):
        self._conn = psycopg2.connect(**self._connection)
        self._cur = self._conn.cursor()

    def get_table(self, schema, name):
        """
        Instantiates and returns a PostgresTable object
        :param schema: The schema of the table
        :param name: The name of the table
        :return: A PostgresTable object
        """
        return PostgresTable(self._cur, schema, name)

    class Factory:
        def connect(self, connection):
            return Postgres(connection)


class PostgresTable(object):

    def __init__(self, cursor, schema, name):
        self._cur = cursor
        self._schema = schema
        self._name = name

    def insert(self, row):
        """
        Inserts a row (as a python dictionary) in to the database table
        NOTE: Needs updating - weak to SQL injection
        :param row: A python dictionary of columns and values
        """
        values = ['%('+e+')s' for e in row.keys()]
        cols = [e for e in row.keys()]
        sql = "insert into %s (%s) values (%s)" % (self._name, ",".join(cols), ",".join(values))
        self._cur.execute(sql, row)

    def delete(self, row):
        """
        Deletes from teh table based on a where clause constructed from
        the row parameter (as a python dictionary)
        NOTE: Needs updating - weak to SQL injection
        :param row: A python dictionary of columns and values
        """
        clause = [e + ' = %('+e+')s' for e in row.keys()]
        sql = "delete from %s  where %s" % (self._name, " and ".join(clause))
        self._cur.execute(sql, row)

    def select(self, row=None):
        """
        Selects data from a table based on a where clause constructed from
        the row parameter (as a python dictionary)
        NOTE: Needs updating - weak to SQL injection
        :param row: A python dictionary of columns and values
        """
        sql = "select * from %s" % (self._name)
        if row is not None:
            clause = [e + ' = %('+e+')s' for e in row.keys()]
            sql = sql + " where %s" % (" and ".join(clause))
        self._cur.execute(sql, row)
        cols = [desc[0] for desc in self._cur.description]
        data = self._cur.fetchall()
        return [dict(zip(cols, row)) for row in data]


class IntegrityError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))


