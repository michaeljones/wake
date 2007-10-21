import sys

from optparse import OptionParser

options = OptionParser()
# options.allow_interspersed_args = False

def report(message):
    """ Writes message to the standard error stream. """

    sys.stderr.write(str(message) + "\n")

