from foundation.activerecord.database import connection
import pipeline

import os
import settings

def setup(shell):
    """
    Configures the environment when a new shell is created.
    """

    # Get previous information from .last file
    home = shell.getenv("HOME")
    last_file = home + os.sep + ".last"
    last = None 
    syntax = ""

    try:
        last = open(last_file, "r")
        syntax = last.readline()
        last.close()
    except IOError:
        pass

    
    # If we've retrieved information from the file
    if syntax:
        levels = settings.hierarchy()

        # Set up a controller and prep it as if we'd called:
        # make <level> <syntax>
        controller_module = __import__("node.controller", globals(), locals(), [None])
        controller = controller_module.NodeController()
        depth = syntax.count(":")
        controller.args = [levels[depth], syntax]
        controller.set()

    # Setup alias for using this module
    shell.alias('pipeline', 'source $PIPELINE/scripts/dispatch.sh node')

    # Add complete (auto-detect controller methds?)


def install():
    """ Creates the node table in the database. """

    # FIXME: Should use exception handling to 
    # catch if table exists already and 
    # alert the user


    db_schema = """
    CREATE TABLE IF NOT EXISTS %snodes (
    id INT UNSIGNED PRIMARY KEY auto_increment,
    name CHAR(16) NOT NULL,
    depth INT NOT NULL,
    parent_id INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL
    ) %s=MYISAM;""" % (settings.table_prefix, connection.engine)

    cursor = connection.cursor()

    table_name = "%snodes" % settings.table_prefix
    print "Creating database table: ", table_name
    cursor.execute_sql(db_schema)


