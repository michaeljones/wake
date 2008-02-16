from sqlalchemy.orm import mapper

class MetaDataMapper(type):
    """Metaclass for the DataMapper class"""

    def __new__(cls, name, bases, dct):
        """
        Creates the DataMapper class along with its
        the "table" class memeber. The table is an 
        instance of the Table class.
        """

        try:
            # If active record isn't a base of the class we're trying to 
            # create then just pass the responsibility up the chain
            # we don't want to do any crazy stuff to non-activerecords
            if not [ c for c in bases if issubclass(c, DataMapper) ]:
                return super(MetaDataMapper, cls).__new__(cls, name, bases, dct) 
        except NameError:
            # If activerecord hasn't been defined yet (then we're probably
            # defining it now so get parent to make it)
            return super(MetaDataMapper, cls).__new__(cls, name, bases, dct)

        class_ = super(MetaDataMapper, cls).__new__(cls, name, bases, dct)

        table = class_.table()
        
        class_.mapper(table)

        return class_


class DataMapper(object):
    """Base class of all model classes."""

    __metaclass__ = MetaDataMapper

    def mapper(cls, table):

        mapper(cls, table)

    mapper = classmethod(mapper)

   


