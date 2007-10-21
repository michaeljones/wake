
class Database(object):
    """
    Base class for all databases classes in the system.
    """

    engine = "ENGINE"

    def quote(self, value):
        """
        Returns the value provided correctly quoted for insertion to the
        database.
        """
        if value == None:
            return "NULL"
        else:
            return "\"" + str(value) + "\""


class Cursor(object):
    """
    Base class for all database cursors. 
    """

    def __init__(self, connection):
        """ Retrieves a standard DB cursor from the connection."""

        self._connection = connection
        self._cursor = connection.cursor()

    def __del__(self):
        """ Closes on the connection."""

        self._connection.close()

    def execute_sql(self, sql):
        """ Executes the sql and returns all the fields via the fetchall() method."""
        self._cursor.execute(sql)
        return self._cursor.fetchall()

    def last_insert_id(self):
        """ Placeholder method for returning id for last inserted entry. """

        return None



