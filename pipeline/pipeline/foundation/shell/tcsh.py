from pipeline.foundation.shell.base import Shell

class Tcsh(Shell):
    """
    Shell class for the TENEX C Shell. 

    Relies on the base class for the interface and
    implementation. This class overrides the template
    strings to be appropriate to Tcsh.
    """

    alias_template = "alias %s '%s';"
    unalias_template = "unalias %s;"
    set_template = "setenv %s '%s';"
    unset_template = "unsetenv %s;"

