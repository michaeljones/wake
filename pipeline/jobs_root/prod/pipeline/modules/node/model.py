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
class Node(ActiveRecord):
    """
    ActiveRecord class for the node module.
    """

    # @staticmethod
    def depth(level):
        """
        Returns the depth of the level provided. For example, if
        hierarchy() returns ['job', 'sequence', 'shot'] then 
        depth("shot") would return 2.
        """

        for index, entry in enumerate(settings.hierarchy()):
            if entry == level:
                return index

        raise InvalidLevel(level)
    
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
        
        env_path = Node.from_env(depth).split(":")
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

        for index, level in enumerate(settings.hierarchy()):
            if index > depth:
                return path
            try:
                path += joiner + shell.getenv("@" + level.upper())
            except EnvVarNotFound:
                if not index == depth:
                    raise PathError(level)
                return path

            joiner = ":"

        return path

    from_env = staticmethod(from_env)

    # @classmethod
    def find_by_syntax(cls, syntax, strict=True):
        """`
        Formulates and executes the SQL necessary to retrieve
        node data from the database given a complete syntax.

        If the syntax refers to nodes that do not exist, the function
        returns None unless "strict" is set to False in which case
        placeholder nodes are returned for any not found in the 
        database.
        """

        # print syntax

        segments = syntax.split(":")

        sql = ""
        internal = "0"
        start = " WHERE "
        levels = settings.hierarchy()
        for index, name in enumerate(segments):
            subquery = start + " ( node.parent_id = ( " + internal + " ) AND node.name = \"" + name + "\" ) \n"
            internal = "SELECT id FROM " + settings.table_prefix + "nodes AS " + levels[index] + " WHERE ( " + levels[index] + ".parent_id = (" + internal + ") AND " + levels[index] + ".name = \"" + name + "\" )" 
            start = "OR "
            sql += subquery

        sql = "SELECT * FROM " + settings.table_prefix + "nodes AS node \n" + sql + " ORDER BY depth"

        records = cls.find_by_sql(sql)
        num_records = len(records)

        
        # sys.stderr.write("\nSQL:\n")
        # sys.stderr.write(sql + "\n")

        # Reverse records so that order matches syntax
        # records.reverse()

        # sys.stderr.write("\nRecords straight from DB:\n")
        # for n in records:
        #     sys.stderr.write(str(n) + "\n")


        if num_records != len(segments): 
            if strict:
                # FIXME: Should throw an exception
                return None
            else:
                # Pad out the end of the record list with 
                # correctly named but otherwise empty node objects
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
                    node = Node(new_record)
                    records.append(node)


        # sys.stderr.write("\nRecords with padding:\n")
        # for n in records:
        #     sys.stderr.write(str(n) + "\n")

       
        node = None
        target = None
        for entry in records:
            if node:
                entry.parent = node
                # FIXME: Added for SQL statements. However it should pick up parent.id
                entry.parent_id = node.id
            else:
                entry.parent =  Node({"name" : "", "id" : 0, "parent" : None })
                entry.parent_id = 0
                # target = entry 
            # else:
            #     node.parent = Node({"name" : "", "id" : 0 })
            #     # FIXME: Added for SQL statements. However it should pick up parent.id
            #     node.parent_id = 0
            node = entry

        # node.parent = Node({"name" : "", "id" : 0 })
        # FIXME: Added for SQL statements. However it should pick up parent.id
        # node.parent_id = 0

        # print "final: ", node

        return node

    find_by_syntax = classmethod(find_by_syntax)


    def file_path(self):
        """
        Returns the complete file path for the node.
        """
 
        path = ""
        joiner = ""
        for n in self.branch():
            path = n.name + joiner + path
            joiner = os.sep

        # sys.stderr.write(str(self.name) + " at " + str(self.depth) + ": " + path + "\n")
        # parent_id = self.parent_id
        # path = self.name
        # tmp_node = self 
        # while parent_id:
        #     tmp_node = tmp_node.parent
        #     parent_id = tmp_node.parent_id
        #     if tmp_node.name:
        #         path = tmp_node.name + os.sep + path

        shell = Shell()
        return shell.getenv('@JOBS_ROOT') + os.sep + path


    def branch(self):
        """
        Returns iterator over the node branch. Starting 
        from the current node and returning the next parent
        in turn up to the top of the path.

        Designed for "for node in instance.branch():" syntax.
        """

        def parent_iter():
            tmp_node = self
            while True:
                yield tmp_node
                if tmp_node.parent_id:
                    tmp_node = tmp_node.parent
                else:
                    raise StopIteration

        return parent_iter()


    def syntax(self):
        """
        Return the complete syntax specifying the node.
        """

        syntax = ""
        joiner = ""
        for node in self.branch():
            syntax = node.name + joiner + syntax
            joiner = ":"

        return syntax


    def destroy_subtree(self):
        """
        Destroys itself and any nodes below it in the hierarchy.
        """

        self.destroy_children()
        self.destroy()


    def destroy_children(self):
        """ 
        Destroys all child nodes of the instance.
        """

        if self.depth == settings.depth():
            # Node is a terminal node and has no children
            return

        sql = "SELECT * FROM " + settings.table_prefix + "nodes"
        internal = str(self.id) + " " 
        comparison = "= "
        joiner = " WHERE"
        
        for i in range(self.depth, len(settings.hierarchy()) - 1, 1):
            sql += joiner + " parent_id " + comparison + internal
            internal = "( SELECT id FROM " + settings.table_prefix + "nodes WHERE parent_id " + comparison + internal + ") "
            joiner = "OR"
            comparison = "IN "

        records = self.find_by_sql(sql)

        # FIXME: Group all deletes together
        # So it's only one SQL call
        for entry in records:
            entry.destroy()


