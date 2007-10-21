
class Field(object):
    """
    Class for a field in a database table.
    """

    def __init__(self, description):
        """
        Sets up an attribute for each element which describes
        the field. Changes the Field entry so that it is accessible
        through the "name" attribute.

        The description comes from the DESCRIBE SQL call.
        """

        for k, v in description.iteritems():
            if k == "Field":
                setattr(self, "name", v)
            else:
                setattr(self, k.lower(), v)

