from foundation.shell.base import Shell

class Bash(Shell):
    """ 
    Shell class for the Bourne Again Shell (Bash)

    Relies on the base class for the interface and
    implementation. This class overrides the template
    strings to be appropriate to Bash.
    """

    alias_template = "alias %s='%s'"
    unalias_templte = "unalias %s"
    set_template = "export %s=%s"
    unset_template = "unset %s "

