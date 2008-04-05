from pipeline.controller.base import ModuleController, FailedRequest
from pipeline.datamapper import session
from pipeline.shell import Shell, EnvVarNotFound
from pipeline import settings
from level.model import Level, InvalidLevel, PathError

import pipeline 
import sys
import shutil
import os
import datetime

class LevelController(ModuleController):
    """ Controller for the level module. """

    allow_invalid_level_for = ["make"]
    scaffold = ['template']

    def syntax_and_depth(self):

        level_name = self.args[0]
        syntax = self.args[1]

        depth = None
        try:
            depth = Level.get_depth(level_name)
        except InvalidLevel, e:
            pipeline.report("Error - Invalid pipeline level: " + str(e))
            raise FailedRequest

        try: 
            syntax = Level.complete_syntax(syntax, depth)
        except PathError:
            pipeline.report("Error - Unable to complete path from environment.")
            raise FailedRequest 


        return syntax, depth



    #
    #   Methods
    #

    def make(self):
        """
        This method is responsible for:
            - Creating the level folder
            - Creating the "share" folder
            - Templating the share folder
            - Entering the level into the database

        It will exit if the level already exists or if the 
        path is in some way invalid.
        """

        # Get full syntax
        syntax, depth = self.syntax_and_depth()

        # Check to see if level exists
        level_list = Level.find_by_syntax(syntax)

        if level_list:
            pipeline.report("Error - Level %s already exists." % syntax)
            return

        # Try to get the parent level
        parent_syntax = ":".join(syntax.split(":")[:-1])

        parent = None

        if parent_syntax:
            # Retrieve parent in a list object
            parent = Level.find_by_syntax(parent_syntax)

            if not parent:
                pipeline.report("Error - Level %s does not exist. Cannot create a child level." % parent_syntax)
                return

            parent = parent[0]

        # Create and setup new level
        new_level = Level()
        new_level.name = syntax.split(":")[-1]
        new_level.parent = parent
        new_level.depth = depth
        new_level.created_at = datetime.datetime.today()

        # Create level folder on disk
        file_path = new_level.file_path()
        os.mkdir(file_path)

        # Create the share folder 
        os.mkdir(file_path + os.sep + "share")

        # Process template
        self.template(new_level)

        # Create the level in the database
        session.save(new_level)
        session.flush()

        # Set up the environment for the level
        self.set()


    def remove(self):
        """
        Removes the level and all it's children from 
        the filesystem and the database.
        """

        # Get full syntax
        syntax, depth = self.syntax_and_depth()

        # Check to see if level exists
        level_list = Level.find_by_syntax(syntax)

        if not level_list:
            pipeline.report("Error - Syntax does not match any levels")
            return

        if len(level_list) > 1:
            pipeline.report("Error - Syntax matches multiple levels")
            return

        level = level_list[0]

        # Get settings info
        hierarchy = settings.hierarchy()
        abbr = settings.abbreviations()

        aliases = ['', 'bin']

        shell = Shell()

        # If we're removing a level in our current environment
        clean_env = True
        for n in level.branch():
            # Check each level of the env against our level branch
            clean_env = True
            try:
                clean_env = (n.name != shell.getenv("@" + hierarchy[n.depth].upper()))
            except EnvVarNotFound:
                clean_env = False
                break

            # Necessary?
            if not clean_env:
                break

        # If necessary unset all environment variables and aliases
        # associated with this level and those below
        if clean_env:
            depth = level.depth
            for level_name in hierarchy[level.depth:]:
                shell.unset("@" + level_name.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1


        # Write out a syntax file so it is up-to-date with current env
        self.write_last(level.parent)

        shell.commit()

        # Remove the level from disk
        shutil.rmtree(level.file_path())

        # Remove the level and all its children from the database
        level.destroy_children()
        session.delete(level)
        session.flush()


    def set(self):
        """ 
        Sets the environment to correspond to this level.
        """
        
        # Get full syntax
        syntax, depth = self.syntax_and_depth()

        # Check to see if level exists
        level_list = Level.find_by_syntax(syntax)

        if not level_list:
            pipeline.report("Error - Syntax does not match any levels")
            return

        if len(level_list) > 1:
            pipeline.report("Error - Syntax matches multiple levels")
            return

        # Get the level we've found
        level = level_list[0]

        shell = Shell()

        # Grab settings info for reference
        hierarchy = settings.hierarchy()
        abbr = settings.abbreviations()

        # Clean out the any pipeline paths from PATH so we can reset it
        pattern = shell.getenv("@JOBS_ROOT") + r'/[\w/]*/share/bin'
        shell.clean('PATH', pattern)

        # Clean prod from PATH as well
        pattern = shell.getenv("@JOBS_ROOT") + r'/prod/[\w/]*'
        shell.clean('PATH', pattern)

        aliases = ['', 'bin']

        # Remove all environment variables and aliases
        # associated with levels below this one
        depth = level.depth + 1
        if level.depth < len(hierarchy) - 1:
            for level_name in hierarchy[level.depth + 1:]:
                shell.unset("@" + level_name.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1
                

        bin_path = ""
        # Set environment from level 
        for l in level.branch():
            shell.set("@" + hierarchy[l.depth], l.name)
            bin_path += "%s/share/bin:" % l.file_path()

        # Set aliases
        cd_path = "cd $@JOBS_ROOT"
        for index, level_name in enumerate(hierarchy[:level.depth + 1]):
            # alias current level
            cd_path += os.sep + "$@" + level_name.upper()
            shell.alias(abbr[index], cd_path)

        prod = shell.getenv("@PROD")
        bin_path += "%s/bin" % prod
        shell.insert("PATH", bin_path)

        self.write_last(level)

        shell.commit()


    def list(self):

        # Get full syntax
        syntax, depth = self.syntax_and_depth()

        # Check to see if level exists
        level_list = Level.find_by_syntax(syntax)

        if not level_list:
            pipeline.report("Error - Syntax does not match any levels")
            return
        
        # TODO: Add option for printing complete paths

        self.view.levels = level_list


    def status(self):

        shell = Shell()

        path = ""
        joiner = ""

        for index, level_name in enumerate(settings.hierarchy()):
            try:
                path += joiner + shell.getenv("@" + level_name.upper())
            except EnvVarNotFound:
                continue

            joiner = ":"

        sys.stderr.write("%s\n" % path)



    #
    #   Utilities
    #
    def write_last(self, level):

        # Write information out to .last file in users HOME
        # Only if it is different to the current one
        # FIXME: Should use shell object
        last_file = os.getenv("HOME") + os.sep + ".last"
        old_syntax = ""
        try:
            last = open(last_file, "r")
            old_syntax = last.readline()
            last.close()
        except IOError:
            pass

        # FIXME: Have to do this test because JOB levels don't have a parent! 
        if level:
            # If new is different to old then write it out
            new_syntax = level.syntax()
            if new_syntax != old_syntax:
                last = open(last_file, "w")
                last.write(level.syntax())
                last.close()




