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

    # Setup alias for using this module
    shell.alias('pdev', 'source $PIPELINE/scripts/dispatch.sh development')


def install():
    """ Creates the development table in the database. """

    pass

