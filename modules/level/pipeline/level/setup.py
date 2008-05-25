from pipeline.level.model import Level
from pipeline.shell import EnvVarNotFound
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

    try:
        last_file = shell.getenv("@LAST_FILE")
    except EnvVarNotFound:
        last_file = os.getenv("HOME") + os.sep + ".last"

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
        controller_module = __import__("pipeline.level.controller", globals(), locals(), [None])
        controller = controller_module.LevelController()
        depth = syntax.count(":")
        args = [hierarchy[depth], syntax]
        controller.set(args)

    # Setup alias for using this module
    shell.alias('pipeline', 'source $PIPELINE/scripts/dispatch.sh level')

    # Add complete (auto-detect controller methds?)


def install():
    """ Creates the level table in the database. """

    print "Running instal for level module"

    # Create table in database
    levels_table = Level.table()
    levels_table.create()

    print "Creating database table:", levels_table.name

    # Adding default settings to pipeline configuration
    source = pkg_resources.resource_filename(__name__, 'etc')

    # Copy over module resources
    module_resources = os.path.join(os.environ["PIPELINE"], "modules", "resources", "level")
    shutil.copytree(source, module_resources)

    os.mkdir(os.path.join(module_resources, "internal"))

    
    config = open(os.path.join(source, "settings.yaml"))
    contents = config.read()
    config.close()

    print "Appending level module defaults to pipeline settings"
    pipeline_settings = os.path.join(os.environ["PIPELINE"], "settings.yaml")
    settings = open(pipeline_settings, "a")
    settings.seek(0, os.SEEK_END)
    settings.write(contents)
    settings.close()




