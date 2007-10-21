import sys
from datetime import datetime

import settings 
from foundation.activerecord.database import connection
from foundation.activerecord.table import Table

class ActiveRecordError(Exception):
    """Base class for all ActiveRecord errors."""
    pass
class RecordNotFound(ActiveRecordError):
    """Error returned when the specified record is not found."""
    pass
class RecordExists(ActiveRecordError):
    """Error returned when attempting to create a record that already exists."""
    pass

class MetaRecord(type):
    """Metaclass for the ActiveRecord class"""

    def __new__(cls, name, bases, dct):
        """
        Creates the ActiveRecord class along with its
        the "table" class memeber. The table is an 
        instance of the Table class.
        """

        try:
            # If active record isn't a base of the class we're trying to 
            # create then just pass the responsibility up the chain
            # we don't want to do any crazy stuff to non-activerecords
            if not [ c for c in bases if issubclass(c, ActiveRecord) ]:
                return super(MetaRecord, cls).__new__(cls, name, bases, dct) 
        except NameError:
            # If activerecord hasn't been defined yet (then we're probably
            # defining it now so get parent to make it)
            return super(MetaRecord, cls).__new__(cls, name, bases, dct)

        # Now must be dealing with a child of activerecord
        # Get table details
        # FIXME: Some of this go into Table constructor?
        table_name = settings.table_prefix + name.lower() + "s"
        cursor = connection.cursor()

        sql = "DESCRIBE " + table_name

        result = cursor.execute_sql(sql)

        class_ = super(MetaRecord, cls).__new__(cls, name, bases, dct)

        class_.table = Table(table_name, result)

        return class_


class ActiveRecord(object):
    """Base class of all model classes."""

    __metaclass__ = MetaRecord

    # @classmethod
    def find(cls, *args, **kwargs):
        """
        Classmethod which mimicks the Ruby on Rails "find" method.
        """

        if args[0] == "first":
            pass
        elif args[0] == "all":
            pass
        else:
            pass

        return # records

    find = classmethod(find)

    # @classmethod
    def find_by_sql(cls, sql):
        """
        Classmethod which executes the given SQL and returns
        any fields retrieved from the database.
        """

        cursor = connection.cursor()
        result = cursor.execute_sql(sql)

        records = []
        for entry in result:
            instance = cls(entry)
            records.append(instance)

        return records

    find_by_sql = classmethod(find_by_sql)

    def __init__(self, record_set=None):
        """
        If a record set is provided, appropriate information
        is extracted and used to set instance variables to 
        the correct values.

        Additionally if any fields are of type "datetime" the 
        equivalent attribute is set to the current time. This
        information is overridden by that in the record set.
        """

        for field in self.table:
            if field.type == "datetime":
                setattr(self, field.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                setattr(self, field.name, None)
        
        if record_set:
            for k, v in record_set.iteritems():
                setattr(self, k, v)

    def __nonzero__(self):
        """
        Magic method for "if instance:" tests. The instance
        returns false if it has no idea and therefore it is assumed
        does not exist in the database.
        """

        if self.id == None:
            return False
        else:
            return True

    def __str__(self):
        """
        Magic method for converting the instance to a string. The 
        class name and field names and values are returned
        """

        return self.__class__.__name__ + " instance (" + " ".join([field + ":" + self._values()[i] for i,field in enumerate(self.table.field_names())]) + ")"

    def _quoted_values(self):
        """
        Returns the values relating to the database entries, quoted as appropriate.
        """
        return [ connection.quote(getattr(self, name)) for name in self.table.field_names()]

    def _values(self):
        """
        Return the values relating to the database entries as unquoted strings.
        """
        return [ str(getattr(self, name)) for name in self.table.field_names()]

    def save(self):
        """
        Not implemented yet.

        Either updates or creates an entry in the database as appropriate. 

        Possibly should not be implemented as it might always be clear whether 
        save or update should be used.
        """
        pass

    def create(self):
        """
        Creates an entry in the database with the instance information. Also retrieves 
        the id of the entry created and assigns it to the instance id attribute.

        Returns RecordExists error if the instance already has an id value. 
        """
        if self.id:
            raise RecordExists
        
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % (self.table, ", ".join(self.table.field_names()), ", ".join(self._quoted_values()))

        cursor = connection.cursor()
        cursor.execute_sql(sql)

        self.id = cursor.last_insert_id()

    def update(self):
        """
        Updates the entry in the database with the same id, to match the instance attributes.
        """
        pass

    def destroy(self):
        """
        Removes the entry with the instance id from the database table.
        """

        sql = "DELETE FROM %s WHERE id = %s;" % (self.table, self.id)

        cursor = connection.cursor()
        cursor.execute_sql(sql)

        


