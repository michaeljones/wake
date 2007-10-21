
def hierarchy():
    """
    Returns a list of the nodes in the structure. 
    Starting at the top.
    """

    return ['job', 'sequence', 'shot', 'element']

def abbreviations():
    """
    Returns a list of the abbreviations for the nodes in the 
    structure. There must be a 1-to-1 ratio with the result
    returned by hierarchy().
    """

    return ['j', 'q', 's', 'e']

def depth():
    """ Returns the (depth - 1) of the hierarchy """

    return len(hierarchy()) - 1

table_prefix = "pl_"
env_prefix = "PL_"

db_user = "pipeline"
db_name = "pipeline"
db_password = "pipeline"

