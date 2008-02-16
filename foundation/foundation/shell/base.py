import os
import re

class ShellError(Exception):
    """Base class for all Shell errors."""
    pass

class EnvVarNotFound(ShellError):
    """
    Error returned when environment variable is 
    not found in either the Shell's env member list or 
    in os.environ.
    """
    pass

# All environment access should go through this class
# Find a nicer way to do all that crazy substitution
class Shell(object):
    """
    Base class for all shell classes. Contains all necessary methods
    but relies on class members being overridden in child classes

    All access and changes to the environment should be done through
    this class. Additionally methods allow for creating aliases. 

    As Python is run as subprocess of the shell, it cannot directly 
    affect the environment of the shell. As a result the output of 
    the script is generally sourced to all it to affect the shell. 
    None of the methods of this class have any direct affect on the shell
    unless the changes are committed using the commit() method and the 
    result is sourced. The commit method prints out all the necessary 
    commands to the standard out to be sourced by the active shell. 

    The class keeps track of the changes it will make to the environment
    so changing an environment variable and querying it later before it 
    has had a chance to be committed will still return the changed result.
    """

    set_template = "Error- base Shell class in use for setenv %s '%s';"
    unset_template = "Error- base Shell class in use for unsetenv %s '%s';"
    alias_template = "Error - base Shell class in use for alias %s '%s';"
    unalias_template = "Error - base Shell class in use for alias %s '%s';"

    commands = []
    env = {}

    def _sub(self, value):
        """
        Returns value. Designed to be overridden to perform any 
        necessary substitutions within "value" before returning it.
        """

        return value 

    def getenv(self, name):
        """
        Returns the value of the environment variable "name"

        Checks within it's own private record for the most up-to-date
        value before checking the actual environment.
        """

        name = self._sub(name)
        try: 
            return self.env[name]
        except KeyError:
            try:
                return os.environ[name]
            except KeyError:
                raise EnvVarNotFound

    def alias(self, name, value):
        """
        Aliases "name" to "value".
        """

        name = self._sub(name)
        value = self._sub(value)

        command = self.alias_template % (name, value)
        self.commands.append(command)

    def unalias(self, name):
        """ Unaliases the alias "name".  """

        name = self._sub(name)

        command = self.unalias_template % name
        self.commands.append(command)

    def clean(self, name, pattern, unset=False):
        """
        Removes any entries (colon separated) in the environment variable
        "name" which match the regex pattern.
        """

        value = self.getenv(name)
        p = re.compile(pattern)
        newvalue = ""
        sep = ""

        for section in value.split(":"):
            # print "#",section
            if not p.match(section):
                newvalue = newvalue + sep + section 
                sep = ":"
            else:
                pass
                # print "# matched", section

        if not newvalue and unset:
            self._unset(name)
        else:
            self._set(name, newvalue)


    def set(self, name, value):
        """ 
        Set the environment variable "name" to "value". This is a 
        wrapper for _set. This method calls _sub on name and value 
        before passing them to _set().
        """

        name = self._sub(name)
        value = self._sub(value)

        self._set(name, value)

    def unset(self, name):
        """ 
        Unsets the environment variable "name". This is a wrapper 
        method for _unset. This method contains a call to _sub 
        before calling _unset.
        """

        name = self._sub(name)

        self._unset(name)

    def _set(self, name, value):
        """ Sets the environment variable "name" to "value". """

        command = self.set_template % (name.upper(), value)
        self.env[name] = value
        self.commands.append(command)

    def _unset(self, name):
        """ Unsets the environment variable "name". """

        command = self.unset_template % name.upper()
        self.env[name] = ""
        self.commands.append(command)

    def insert(self, name, value):
        """
        Inserts the string "value" at the start of the environment
        variable "name". Separating with a colon where necessary.
        """

        name = self._sub(name)
        value = self._sub(value)

        name = name.upper()
        try:
            current_value = ":" + self.getenv(name)
        except EnvVarNotFound:
            current_value = ""

        if current_value:
            value = "%s%s" % (value, current_value)

        self._set(name, value)

    def append(self, name, value):
        """
        Appends the string "value" at the end of the environment
        variable "name". Separating with a colon where necessary.
        """

        name = self._sub(name)
        value = self._sub(value)

        name = name.upper()
        current_value = self.getenv(name)

        if current_value:
            value = "%s:%s" % (current_value, value)

        self._set(name, value)

    def commit(self):
        """
        Prints all the queued commands to standard out via the print builtin. 
        """

        for command in self.commands:
            print command


