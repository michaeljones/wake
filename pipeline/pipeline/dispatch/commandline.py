from foundation.frontcontroller.base import FrontController
from pipeline.controller.base import FailedRequest
from pipeline import options

import pipeline
import sys

class CommandlineController(FrontController):

    def _options(self):
        """ Adds necessary options for the command line. """

        options.add_option("-v", "--verbose", action="store_true", dest="verbose")

    def __init__(self):
        """ Calls _options() """

        # setup default path for the option parser
        self._options()

    def process_request(self):
        """
        Processes the commandline retrieving and calling
        the necessary methods from the necessary classes.
        """

        opts, args = options.parse_args()
        package_name = args[0]

        # Remove package name
        del args[0]

        module_name = package_name + ".controller"

        module = None
        try:
            module = __import__(module_name, globals(), locals(), [None])
        except ImportError, e:
            pipeline.report("Error - Unable to import module \"" + module_name + "\". Import error given:")
            pipeline.report("           %s" % e)
            return

        controller_name = package_name.capitalize() + "Controller"
        
        ControllerClass = None
        try:
            ControllerClass = getattr(module, controller_name) 
        except AttributeError:
            pipeline.report("Error - Unable to find controller in module \"" + module_name + "\"")
            return
        
        controller = ControllerClass()

        try:
            controller.process_request(args)
        except FailedRequest:
            pass

 
