from pipeline.interface.commandline import CommandlineInterface
from pipeline.development.controller import DevelopmentController
from optparse import OptionParser

import sys

class DevelopmentCommandlineInterface(CommandlineInterface):

    name = "Development"
    
    def make(self, args):

        controller = DevelopmentController()
        controller.make(args)

