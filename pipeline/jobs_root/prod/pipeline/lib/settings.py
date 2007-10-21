from pipeline.defaults import *

# Names of the levels of the pipeline hierarchy
# The top level comes first. 
# The number of levels is flexible per pipeline install, but fixed for 
# all projects within that pipeline
def hierarchy():
    return ['job', 'sequence', 'shot', 'element', 'extra']


# Abbreviations for aliased shortcuts
# Must match up with the levels return by hierachy()
def abbreviations():
    return ['j', 'q', 's', 'e', 'x']


def depth():
    """ Returns the (depth - 1) of the hierarchy """

    return len(hierarchy()) - 1

# Prefix for pipeline database tables
table_prefix = "pl_"

# Prefix for pipeline environment variables
env_prefix = "PL_"

# Database name, user and host settings
db_user = "pipeline"
db_name = "pipeline"
db_password = "pipeline"
db_host = "localhost"

