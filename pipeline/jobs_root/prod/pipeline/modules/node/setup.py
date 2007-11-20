from foundation.activerecord.database import connection

import settings

def setup(shell):
    """
    Configures the environment when a new shell is created.
    """

    pass


def install():
    """ Creates the node table in the database. """

    db_schema = """
    CREATE TABLE IF NOT EXISTS %snodes (
    id INT(10) UNSIGNED PRIMARY KEY auto_increment,
    name char(20) NOT NULL
    ) %s=MYISAM;""" % (settings.table_prefix, connection.engine)

    cursor = connection.cursor()

    table_name = "%snodes" % settings.table_prefix
    print "Creating database table:", table_name
    cursor.execute_sql(db_schema)

