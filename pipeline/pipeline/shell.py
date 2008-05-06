import os
import re

from pipeline.foundation.shell.base import EnvVarNotFound
from pipeline import settings

_shell_name = os.getenv("SHELL").split(os.sep)[-1]
_shell_module = __import__("pipeline.foundation.shell." + _shell_name, globals(), locals(), [None])
_Shell = getattr(_shell_module, _shell_name.capitalize())

class Shell(_Shell):
    """ Shell class with pipeline specific _sub function.  """

    # FIXME: Running sub on \@ with PREFIX gives \\PREFIX 
    # Need a way of escaping @ symbols
    env_sub = re.compile(r'@')

    def _sub(self, value):
        """ 
        Returns value with any non-escaped @ symbol substituted with env_prefix 
        settings value.
        """

        return self.env_sub.sub(settings.env_prefix, value)

    def commit(self):
        """
        Prints all the queued commands to standard out via the print builtin. 

        If the PIPELINE_DEBUG environment variable is set then all the commands
        will also be echoed for debugging purposes.
        """

        debug = None
        try:
            debug = self.getenv("PIPELINE_DEBUG")
        except EnvVarNotFound:
            pass

        for command in self.commands:
            if debug:
                print "echo " + command
            print command



