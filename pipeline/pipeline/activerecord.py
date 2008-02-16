from foundation.activerecord import *

import settings

db_address = "mysql://%s:%s@%s/%s" % (settings.db_user, 
                                            settings.db_password, 
                                            settings.db_host, 
                                            settings.db_name)

metadata.bind = db_address

def tablename(cls):

    return '%s%s' % (settings.table_prefix, cls.__name__.lower())

