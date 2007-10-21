from foundation.activerecord.field import Field
import sys

class Table(object):
    """
    Class representing the structure of a database table.
    """

    def __init__(self, name, description):
        """
        Breaks down the description and creates a Field instance
        for each field in the table.
        """

        self._name = name
        self._fields = []

        for entry in description:
            field = Field(entry)
            setattr(self, entry["Field"], field)
            self._fields.append(field)

    def __str__(self):
        """ Returns the tables name. """

        return self._name

    def __iter__(self):
        """ Returns a TableIter instance for iterating over the table."""

        def table_iter():

            if not self._fields:
                raise StopIteration

            index = 0

            while True:
                try:
                    yield self._fields[index]
                    index += 1
                except IndexError:
                    raise StopIteration

        return table_iter()

    def field_names(self):
        """ Returns a list of the field names."""

        return [ f.name for f in self._fields ]

    def quoted_field_names(self):
        """ Returns a list of the field names in quotes."""

        return [ "\"" + f.name + "\"" for f in self._fields ] 

        


