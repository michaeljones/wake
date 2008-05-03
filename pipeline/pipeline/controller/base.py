from pipeline.view.base import View

import pipeline

class FailedRequest(Exception):
    pass

class ModuleController(object):
    """
    Base class for all module controllers.

    Provides default empty definitions for necessary 
    class attributes.
    """

    args = []


