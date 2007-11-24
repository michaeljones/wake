from foundation.activerecord.base import ActiveRecord
from foundation.activerecord.database import connection

from pipeline.shell import Shell, EnvVarNotFound
import pipeline
import settings

import os
import sys

class InvalidLevel(Exception):
    """ Error returned when an invalid level is specified.  """

    # FIXME: Exception base class already provides this functionality?
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PathError(Exception):
    """ 
    Error returned when it is impossible to form a complete
    path from the environment and any provided syntax.
    """
    pass


# FIXME: Add PROD level as level 0
# FIXME: Depth of job should be 1, prod should be 0?
class Level(ActiveRecord):
    """
    ActiveRecord class for the level module.
    """

    # @staticmethod
    def depth(level_name):
        """
        Returns the depth of the level provided. For example, if
        hierarchy() returns ['job', 'sequence', 'shot'] then 
        depth("shot") would return 2.
        """

        for index, entry in enumerate(settings.hierarchy()):
            if entry == level_name:
                return index

        raise InvalidLevel(level_name)
    
    depth = staticmethod(depth)

    # @staticmethod
    def complete_syntax(syntax, depth):
        """
        Given a partial or complete syntax, a complete syntax
        will be returned will all necessary gaps filled in from 
        the environment.
        """

        count = syntax.count(":")
        syntax = ":" * (depth - count) + syntax 
        
        env_path = Level.from_env(depth).split(":")
        segments = syntax.split(":")

        joiner = ""
        path = ""
        for i in range(0, depth + 1, 1):
            if segments[i]:
                path += joiner + segments[i]
            else:
                path += joiner + env_path[i]
            joiner = ":"

        return path

    complete_syntax = staticmethod(complete_syntax)

    # @staticmethod
    def from_env(depth):
        """
        Returns the syntax up to "depth" as is currently
        set in the environment.
        """

        shell = Shell()

        path = ""
        joiner = ""

        for index, level_name in enumerate(settings.hierarchy()):
            if index > depth:
                return path
            try:
                path += joiner + shell.getenv("@" + level_name.upper())
            except EnvVarNotFound:
                if not index == depth:
                    raise PathError(level_name)
                return path

            joiner = ":"

        return path

    from_env = staticmethod(from_env)

    # @classmethod
    def find_by_syntax(cls, syntax, strict=True):
        """`
        Formulates and executes the SQL necessary to retrieve
        level data from the database given a complete syntax.

        If the syntax refers to levels that do not exist, the function
        returns None unless "strict" is set to False in which case
        placeholder levels are returned for any not found in the 
        database.
        """

        segments = syntax.split(":")

        sql = ""
        internal = "0"
        start = " WHERE "
        hierarchy = settings.hierarchy()
        for index, name in enumerate(segments):
            comparison = "="
            name = name.replace("+", "%")
            if name.count("%"):
                comparison = "LIKE"
            subquery = start + " ( level.parent_id = ( " + internal + " ) AND level.name " + comparison + " \"" + name + "\" ) \n"
            internal = "SELECT id FROM " + settings.table_prefix + "levels AS " + hierarchy[index] + " WHERE ( " + hierarchy[index] + ".parent_id = (" + internal + ") AND " + hierarchy[index] + ".name " + comparison + " \"" + name + "\" )" 
            start = "OR "
            sql += subquery

        sql = "SELECT * FROM " + settings.table_prefix + "levels AS level \n" + sql + " ORDER BY depth"

        sys.stderr.write( sql + "\n" )

        records = cls.find_by_sql(sql)
        num_records = len(records)

        sys.stderr.write( str(records) + "\n" )

        levels = Level.link(records)

        return levels
        
        if num_records != len(segments): 
            if strict:
                # FIXME: Should throw an exception
                return None
            else:
                # Pad out the end of the record list with 
                # correctly named but otherwise empty level objects
                for i in range(num_records, len(segments), 1):
                    new_record = { "name" : segments[i],
                                   "depth" : i }
                    if records:
                       # FIXME: Should pick up parent.id
                       new_record["parent_id"] = records[i-1].id
                       new_record["parent"] = records[i-1]  
                    else:
                       new_record["parent_id"] = 0 
                       new_record["parent"] = None 
                    level = Level(new_record)
                    records.append(level)

        level = None
        target = None
        for entry in records:
            if level:
                entry.parent = level
                # FIXME: Added for SQL statements. However it should pick up parent.id
                entry.parent_id = level.id
            else:
                entry.parent =  Level({"name" : "", "id" : 0, "parent" : None })
                entry.parent_id = 0
                # target = entry 
            # else:
            #     level.parent = Level({"name" : "", "id" : 0 })
            #     # FIXME: Added for SQL statements. However it should pick up parent.id
            #     level.parent_id = 0
            level = entry

        # level.parent = Level({"name" : "", "id" : 0 })
        # FIXME: Added for SQL statements. However it should pick up parent.id
        # level.parent_id = 0

        # print "final: ", level

        return level

    find_by_syntax = classmethod(find_by_syntax)

    
    def link(self, levels):

        indexed = {}
        compressed = {}

        for level in levels:
            indexed[level.id] = level
            compressed[level.id] = level

        for i, level in enumerate(levels):
            
            if indexed.has_key(level.parent_id):
                level.parent = indexed[level.parent_id]
                compressed.pop(level.parent_id, None)

        return compressed.items()

    link = staticmethod(link)

    def find_children(self):

        return


    def file_path(self):
        """
        Returns the complete file path for the level.
        """
 
        path = ""
        joiner = ""
        for n in self.branch():
            path = n.name + joiner + path
            joiner = os.sep

        # sys.stderr.write(str(self.name) + " at " + str(self.depth) + ": " + path + "\n")
        # parent_id = self.parent_id
        # path = self.name
        # tmp_level = self 
        # while parent_id:
        #     tmp_level = tmp_level.parent
        #     parent_id = tmp_level.parent_id
        #     if tmp_level.name:
        #         path = tmp_level.name + os.sep + path

        shell = Shell()
        return shell.getenv('@JOBS_ROOT') + os.sep + path


    def branch(self):
        """
        Returns iterator over the level branch. Starting 
        from the current level and returning the next parent
        in turn up to the top of the path.

        Designed for "for level in instance.branch():" syntax.
        """

        def parent_iter():
            tmp_level = self
            while True:
                yield tmp_level
                if tmp_level.parent_id:
                    tmp_level = tmp_level.parent
                else:
                    raise StopIteration

        return parent_iter()


    def syntax(self):
        """
        Return the complete syntax specifying the level.
        """

        syntax = ""
        joiner = ""
        for level in self.branch():
            syntax = level.name + joiner + syntax
            joiner = ":"

        return syntax


    def destroy_subtree(self):
        """
        Destroys itself and any levels below it in the hierarchy.
        """

        self.destroy_children()
        self.destroy()


    def destroy_children(self):
        """ 
        Destroys all child levels of the instance.
        """

        if self.depth == settings.depth():
            # Level is a terminal level and has no children
            return

        sql = "SELECT * FROM " + settings.table_prefix + "levels"
        internal = str(self.id) + " " 
        comparison = "= "
        joiner = " WHERE"
        
        for i in range(self.depth, len(settings.hierarchy()) - 1, 1):
            sql += joiner + " parent_id " + comparison + internal
            internal = "( SELECT id FROM " + settings.table_prefix + "levels WHERE parent_id " + comparison + internal + ") "
            joiner = "OR"
            comparison = "IN "

        records = self.find_by_sql(sql)

        # FIXME: Group all deletes together
        # So it's only one SQL call
        for entry in records:
            entry.destroy()


