from foundation.actioncontroller.base import MetaController as _MetaController
from foundation.actioncontroller.base import ActionController

from pipeline.view.base import View

import pipeline
import scaffold

class FailedRequest(Exception):
    pass

class MetaController(_MetaController):
    """
    Metaclass for the module controller.

    Inherits from actioncontroller.base.Metacontroller however 
    it overrides the only defined method.
    """
   
    def __new__(cls, name, bases, dct):
        """
        Reads the scaffold class attribute and copies in 
        methods from the scaffold module that match the 
        strings found the scaffold list.
        """

        try:
           # If active record isn't a base of the class we're trying to 
           # create then just pass the responsibility up the chain
           # we don't want to do any crazy stuff to non-activerecords
           if not [ c for c in bases if issubclass(c, ActionController) ]:
               return super(MetaController, cls).__new__(cls, name, bases, dct) 
        except NameError:
           # If activerecord hasn't been defined yet (then we're probably
           # defining it now so get parent to make it)
           return super(MetaController, cls).__new__(cls, name, bases, dct)

        # Now must be dealing with a child of ActionController
        class_ = super(MetaController, cls).__new__(cls, name, bases, dct)

        for method in class_.scaffold:
            setattr(class_, method, getattr(scaffold, method))

        return class_


class ModuleController(ActionController):
    """
    Base class for all module controllers.

    Provides default empty definitions for necessary 
    class attributes.
    """

    __metaclass__ = MetaController

    scaffold = []
    args = []


