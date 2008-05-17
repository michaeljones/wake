import sys
import os
import pkg_resources

def report(message):
    """ Writes message to the standard error stream. """

    sys.stderr.write(str(message) + "\n")

def etc():
    return pkg_resources.resource_filename("pipeline.core", 'etc')

