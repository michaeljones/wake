from level.model import Level
import pipeline

import os
import sys
import shutil
import pkg_resources
import pipeline.settings

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
        hierarchy = pipeline.settings.hierarchy()

        # Set up a controller and prep it as if we'd called:
        # make <level> <syntax>
        controller_module = __import__("level.controller", globals(), locals(), [None])
        controller = controller_module.LevelController()
        depth = syntax.count(":")
        args = [hierarchy[depth], syntax]
        controller.set(args)

    # Setup alias for using this module
    shell.alias('pipeline', 'source $PIPELINE/scripts/dispatch.sh level')

    # Add complete (auto-detect controller methds?)


def install():
    """ Creates the level table in the database. """

    # Create table in database
    levels_table = Level.table()
    levels_table.create()

    print "Creating database table:", levels_table.name


    # Copy over module resources
    module_resources = os.path.join(os.environ["PIPELINE"], "modules", "resources", "level")
    source = pkg_resources.resource_filename(__name__, 'etc')
    shutil.copytree(source, module_resources)

    os.mkdir(os.path.join(module_resources, "internal"))


