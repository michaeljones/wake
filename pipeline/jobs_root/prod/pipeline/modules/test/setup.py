import settings
import sys

def setup(shell):
    """
    Sets up test aliases
    """

    # Setup alias for using this module
    shell.alias('ptest', 'source $PIPELINE/test/pipelineTest.tcsh')


def install():
    """
    Does nothing
    """

    pass


