from foundation.activerecord.database.base import Database
from foundation.activerecord.database.base import Cursor
import settings

import MySQLdb
import MySQLdb.cursors
import datetime

# Should only be one instance of this created in the 
# MySQL object
# FIXME: Singleton pattern?
class MySQLCursor(Cursor):
    """
    Cursor object for interaction with the database.
    
    Provides a basic wrapper around the MySQLdb cursor
    """

    def last_insert_id(self):
        """ Returns the id of the last entry inserted into the database. """

        return self.execute_sql("SELECT LAST_INSERT_ID() AS id;")[0]["id"]


class MySQL(Database):
    """
    Class for interacting with the datebase.

    Basic wrapper around the MySQLdb methods.
    """

    def __init__(self):
        self._connection = None
        self._cursor = None

    def cursor(self):
        """
        If necessary sets up the connection and returns a cursor.
        """

        if not self._connection:
            self._connection = MySQLdb.connect( 
                    host = settings.db_host,
                    user = settings.db_user,
                    passwd = settings.db_password,
                    db = settings.db_name,
                    cursorclass = MySQLdb.cursors.DictCursor)

        if not self._cursor:
            self._cursor = MySQLCursor(self._connection)

        return self._cursor

    def close(self):
        """Closes the connection."""

        self._connection.close()


    # FIXME: Add some kind of function that returns the function
    # or just make sure the module sets the right values for the version (ENGINE/TYPE=MYISAM)

