from pipeline.datamapper.base import DataMapper
from pipeline.datamapper import session, metadata, mapper, relation, select
from pipeline.datamapper import and_, or_
from pipeline.datamapper import Table, Column, String, Integer, DateTime, ForeignKey
from pipeline.shell import Shell, EnvVarNotFound

import pipeline
import pipeline.settings

import os
import sys

class InvalidLevel(Exception):
    """ Error returned when an invalid level is specified.  """
    pass

class PathError(Exception):
    """ 
    Error returned when it is impossible to form a complete
    path from the environment and any provided syntax.
    """
    pass


# FIXME: Add PROD level as level 0
# FIXME: Depth of job should be 1, prod should be 0?
class Level(DataMapper):
    """
    Datamapper class for the level module.
    """

    def table(cls):

        try:
            return cls._table
        except AttributeError:
            pass

        table_name = "%slevels" % pipeline.settings.table_prefix

        cls._table = Table(table_name, metadata,
                          Column('id', Integer, primary_key=True),
                          Column('name', String(50)),
                          Column('depth', Integer),
                          Column('parent_id', Integer, ForeignKey("%s.id" % table_name)),
                          Column('created_at', DateTime) 
                          )

        return cls._table

    table = classmethod(table)

    def mapper(cls, table):

        mapper(cls, table, properties={
                                'parent':relation(cls, remote_side=[table.c.id])
                                })

    mapper = classmethod(mapper)

    # @staticmethod
    def get_depth(level_name):
        """
        Returns the depth of the level provided. For example, if
        hierarchy() returns ['job', 'sequence', 'shot'] then 
        depth("shot") would return 2.
        """

        for index, entry in enumerate(pipeline.settings.hierarchy()):
            if entry == level_name:
                return index

        raise InvalidLevel(level_name)
    
    get_depth = staticmethod(get_depth)

    # @staticmethod
    def complete_syntax(syntax, depth):
        """
        Given a partial or complete syntax, a complete syntax
        will be returned will all necessary gaps filled in from 
        the environment.
        """

        env_path = Level.from_env(depth).split(":")

        if not syntax:
            return env_path

        count = syntax.count(":")
        syntax = ":" * (depth - count) + syntax 
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

        for index, level_name in enumerate(pipeline.settings.hierarchy()):
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

        query = session.query(Level)
        ors = []

        for i in range(len(segments)-1, -1, -1):

            name = segments[i].replace("+", "%")
            if name.count("%"):
                name_condition = Level.name.like(name)
            else:
                name_condition = Level.name==segments[i]

            if i == len(segments)-1:
                query = query.filter(and_(name_condition, Level.depth==i))
            if i == len(segments) - 2:
                query = query.join('parent', aliased=True).filter(and_(name_condition, Level.depth==i))
            if i < len(segments) - 2:
                query = query.join('parent', aliased=True, from_joinpoint=True).filter(and_(name_condition, Level.depth==i))

        # sys.stderr.write("Query: " + str(query) + "\n")
        results = query.all()

        return results


    find_by_syntax = classmethod(find_by_syntax)

    
    # @staticmethod
    def link(levels):

        if not levels:
            return levels

        indexed = {}
        compressed = {}

        # Ideally this would be named "prod" however that causes some syntax problems
        # especially in the .last file write
        prod =  Level({"name" : "",
                       "id" : 0,
                       "depth" : -1,
                       "parent" : None })

        indexed[0] = prod
        compressed[0] = prod

        for level in levels:
            indexed[level.id] = level
            compressed[level.id] = level


        for i, level in enumerate(levels):
            
            if indexed.has_key(level.parent_id):
                level.parent = indexed[level.parent_id]
                compressed.pop(level.parent_id, None)

        return compressed.values()

    link = staticmethod(link)


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
                if tmp_level.parent:
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


    def destroy_children(self):
        """ 
        Destroys all child levels of the instance.
        """

        if self.depth == pipeline.settings.depth():
            # Level is a terminal level and has no children
            return

        query = session.query(Level)

        #  subquery = select([Taggable.c.id], query._criterion,
        #                           from_obj= query._from_obj).as_scalar()

        # query = query.filter( )
        filters = []
        subquery = Level.parent_id==self.id
        final = subquery

        # Somehow this shit works!
        for i in range(self.depth, len(pipeline.settings.hierarchy()) - 1, 1):
            alias = Level._table.alias()
            subquery = Level.parent_id.in_(select([alias.c.parent_id], subquery))
            final = final | subquery

        query = query.filter(final)

        level_list = query.all()

        # Must be a better way of doing this!
        for level in level_list:
            session.delete(level)

        session.flush()


