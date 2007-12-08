import settings
import sys

def setup(shell):
    """
    Sets up test aliases
    """

    # Setup alias for using this module
    shell.alias('psource', 'source $PIPELINE/test/pipelineTest.tcsh')

    shell.alias('ptest', 'source $PIPELINE/scripts/dispatch.sh test')

def install():
    """
    Does nothing
    """

    pass


