import shutil

class MetaController(type):
   
    def __new__(cls, name, bases, dct):
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

        return class_

class Empty(object):
    pass

class ActionController(object):
    """
    Base class for all controllers.
    """

    def __init__(self):
        self.view = Empty()

