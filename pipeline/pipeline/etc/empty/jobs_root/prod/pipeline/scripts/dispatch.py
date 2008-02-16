#!/usr/bin/python -tt

import sys

from pipeline.dispatch.commandline import CommandlineController

# As the output of this script is designed to
# be sourced. Make sure that if nothing else
# is provided, it at least has a blank line to "run"
print "echo -n;"

dispatcher = CommandlineController()

dispatcher.process_request()

