from foundation.datamapper import *
from pipeline.shell import Shell

import pipeline.settings
import os
import sys

# db_address = "mysql://%s:%s@%s/%s" % (settings.db_user,
#                                             settings.db_password,
#                                             settings.db_host,
#                                             settings.db_name)


shell = Shell()
pipeline_folder = shell.getenv("PIPELINE")

db_file = os.path.join(pipeline_folder, "db", "pipeline.db")

# Triple slash for absolute path
db_address = "sqlite:///%s" % db_file


db = create_engine(db_address)

# db.echo = True

metadata = MetaData(db)

session = create_session()


