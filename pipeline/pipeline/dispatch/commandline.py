from pipeline.controller.base import FailedRequest
from optparse import OptionParser

import pipeline
import sys

class CommandlineController(object):

    def process_request(self):
        """
        Processes the commandline retrieving and calling
        the necessary methods from the necessary classes.
        """

        options = OptionParser()

        opts, args = options.parse_args()

        # Remove "dispatch"
        del args[0] 

        package_name = args[0]

        # Remove package name
        del args[0]

        module_name = package_name + ".interface.commandline"

        module = None
        try:
            module = __import__(module_name, globals(), locals(), [None])
        except ImportError, e:
            pipeline.report("Error - Unable to import module \"" + module_name + "\". Import error given:")
            pipeline.report("           %s" % e)
            return

        interface_name = package_name.capitalize() + "CommandlineInterface" 

        InterfaceClass = None
        try:
            InterfaceClass = getattr(module, interface_name) 
        except AttributeError:
            pipeline.report("Error - Unable to find " + interface_name + " in module \"" + module_name + "\"")
            return
        

        interface = InterfaceClass()

        try:
            interface.process_request(args)
        except FailedRequest:
            pass

 
