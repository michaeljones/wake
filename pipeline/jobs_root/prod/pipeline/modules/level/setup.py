from sqlalchemy import Table, Column, Integer, String, Datatime
from pipleine.database import metadata
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
        hierarchy = settings.hierarchy()

        # Set up a controller and prep it as if we'd called:
        # make <level> <syntax>
        controller_module = __import__("level.controller", globals(), locals(), [None])
        controller = controller_module.LevelController()
        depth = syntax.count(":")
        controller.args = [hierarchy[depth], syntax]
        controller.set()

    # Setup alias for using this module
    shell.alias('pipeline', 'source $PIPELINE/scripts/dispatch.sh level')

    # Add complete (auto-detect controller methds?)


def install():
    """ Creates the level table in the database. """

    # FIXME: Should use exception handling to 
    # catch if table exists already and 
    # alert the user


    db_schema = """
    CREATE TABLE IF NOT EXISTS %slevels (
    id INT UNSIGNED PRIMARY KEY auto_increment,
    name CHAR(16) NOT NULL,
    depth INT NOT NULL,
    parent_id INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL
    ) %s=MYISAM;""" % (settings.table_prefix, connection.engine)

    cursor = connection.cursor()

    table_name = "%slevels" % settings.table_prefix
    print "Creating database table:", table_name
    cursor.execute_sql(db_schema)


