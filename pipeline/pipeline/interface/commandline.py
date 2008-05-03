from pipeline.interface.base import Interface
from pipeline.controller.base import FailedRequest
from pipeline.view.commandline import CommandlineView

import pipeline
import sys

class CommandlineInterface(Interface):

    def process_request(self, args):

        method_name = args[0]

        # Remove method name
        del args[0] 

        # self.args = args

        try:
            method = getattr(self, method_name)
        except AttributeError:
            pipeline.report("Error - Invalid method: %s" % method_name)
            return

        # method()
        self._call(method, args)


    def _call(self, method, args):

        try:
            method(args)
        except FailedRequest:
            return

        if hasattr(self, 'view'):
            view = CommandlineView()
            module_name = self.__class__.__name__.replace("CommandlineInterface", "").lower()
            view.execute(method.__name__, module_name, self.__dict__)


